from app.repositories.project_repository import ProjectRepository
from app.schemas.project_schema import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse, ProjectVisibilityUpdate
from app.utils.github_utils import fetch_github_data
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)

class ProjectService:
    def __init__(self, db: Session):
        self.repository = ProjectRepository(db)

    async def create_project(self, project_data: ProjectCreate) -> ProjectResponse:
        """Create a new project, with special handling for GitHub projects"""
        logger.info(f"Creating project: {project_data.title}")
        
        # Convert to dict before passing to repository to avoid pydantic validation errors
        project_dict = project_data.model_dump()
        
        # If it's a GitHub project, enrich data from GitHub API
        if project_data.type == "github" and project_data.url:
            try:
                # Fetch GitHub data
                basic_data, github_full_data = await fetch_github_data(project_data.url)
                
                # Only update fields that are not explicitly provided by the user
                if not project_data.title or project_data.title == "":
                    project_dict["title"] = basic_data["title"]
                
                if not project_data.description or project_data.description == "":
                    project_dict["description"] = basic_data["description"]
                
                # Set expiry date for 1 day from now (using timezone-aware datetime)
                project_dict["expiry_date"] = datetime.now(timezone.utc) + timedelta(days=1)
                
                # Store the complete GitHub response
                project_dict["additional_data"] = github_full_data
                
            except Exception as e:
                logger.error(f"Error fetching GitHub data: {str(e)}")
                # Continue with the data provided by the user
        
        # Create the project
        project = self.repository.create(project_dict)
        
        # Return the created project
        return ProjectResponse.model_validate(project)

    async def refresh_github_data(self, project_id: uuid.UUID) -> Optional[ProjectResponse]:
        """
        Refresh GitHub data for a project.
        
        Args:
            project_id: The ID of the project to refresh
            
        Returns:
            Updated project or None if project not found or not a GitHub project
        """
        logger.info(f"Refreshing GitHub data for project ID: {project_id}")
        
        # Get the project
        project = self.repository.get_by_id(project_id)
        if not project:
            logger.warning(f"Project with ID {project_id} not found")
            return None
            
        # Check if it's a GitHub project
        if project.type != "github" or not project.url:
            logger.warning(f"Project with ID {project_id} is not a GitHub project or has no URL")
            return None
            
        try:
            # Fetch fresh GitHub data
            _, github_full_data = await fetch_github_data(project.url)
            
            # Update project data with timezone-aware datetime
            update_data = {
                "additional_data": github_full_data,
                "expiry_date": datetime.now(timezone.utc) + timedelta(days=1)
            }
            
            # Update the project
            updated_project = self.repository.update(project_id, update_data)
            return ProjectResponse.model_validate(updated_project)
            
        except Exception as e:
            logger.error(f"Error refreshing GitHub data for project {project_id}: {str(e)}")
            return None

    async def get_projects(self, skip: int = 0, limit: int = 100, only_visible: bool = False) -> ProjectListResponse:
        """Get projects with optional filtering by visibility and automatic refresh for GitHub projects"""
        logger.info(f"Retrieving projects (skip={skip}, limit={limit}, only_visible={only_visible})")
        
        # Get projects based on visibility filter
        if only_visible:
            projects = self.repository.get_visible(skip, limit)
            total = self.repository.count_visible()
        else:
            projects = self.repository.get_all(skip, limit)
            total = self.repository.count()
        
        # Check for expired GitHub projects and refresh them
        now = datetime.now(timezone.utc)
        processed_projects = []
        
        for project in projects:
            # Check if this is a GitHub project with an expiry date in the past
            if (project.type == "github" and project.expiry_date and project.expiry_date.replace(tzinfo=timezone.utc) < now):
                try:
                    # Try to refresh the project data
                    updated_project = await self.refresh_github_data(project.id)
                    if updated_project:
                        # Use the updated project
                        processed_projects.append(updated_project)
                    else:
                        # If refresh failed, use the original project
                        processed_projects.append(ProjectResponse.model_validate(project))
                except Exception as e:
                    logger.error(f"Error refreshing expired project {project.id}: {str(e)}")
                    # Use the original project if refresh fails
                    processed_projects.append(ProjectResponse.model_validate(project))
            else:
                # For non-expired or non-GitHub projects, just use the project as is
                processed_projects.append(ProjectResponse.model_validate(project))
        
        return ProjectListResponse(
            projects=processed_projects,
            total=total
        )

    async def get_project(self, project_id: uuid.UUID, only_visible: bool = False) -> Optional[ProjectResponse]:
        """Get a project by ID with automatic refresh if expired"""
        logger.info(f"Retrieving project with ID: {project_id}, only_visible={only_visible}")
        
        # Get the project based on visibility filter
        if only_visible:
            project = self.repository.get_visible_by_id(project_id)
        else:
            project = self.repository.get_by_id(project_id)
            
        if not project:
            return None
            
        # Check if this is a GitHub project with an expiry date in the past
        now = datetime.now(timezone.utc)
        if (project.type == "github" and project.expiry_date and project.expiry_date.replace(tzinfo=timezone.utc) < now):
            try:
                # Try to refresh the project data
                updated_project = await self.refresh_github_data(project.id)
                if updated_project:
                    return updated_project
            except Exception as e:
                logger.error(f"Error refreshing expired project {project.id}: {str(e)}")
                # Continue with the original project if refresh fails
        
        # Return the project (either original or couldn't be refreshed)
        return ProjectResponse.model_validate(project)

    async def update_project(self, project_id: uuid.UUID, project_data: ProjectUpdate) -> Optional[ProjectResponse]:
        """Update a project"""
        logger.info(f"Updating project with ID: {project_id}")
        
        # Convert to dict before passing to repository
        project_dict = project_data.model_dump(exclude_unset=True)
        
        # Get current project
        project = self.repository.get_by_id(project_id)
        if not project:
            return None
            
        # If project type is being changed to "github" and URL is provided, fetch GitHub data
        if "type" in project_dict and project_dict["type"] == "github" and "url" in project_dict:
            try:
                # Fetch GitHub data
                _, github_full_data = await fetch_github_data(project_dict["url"])
                project_dict["additional_data"] = github_full_data
                project_dict["expiry_date"] = datetime.now(timezone.utc) + timedelta(days=1)
            except Exception as e:
                logger.error(f"Error fetching GitHub data: {str(e)}")
                # Continue with update without GitHub data
                
        # If project type is changed to "custom", remove expiry date
        if "type" in project_dict and project_dict["type"] == "custom":
            project_dict["expiry_date"] = None
        
        # Update the project
        updated_project = self.repository.update(project_id, project_dict)
        
        if updated_project:
            return ProjectResponse.model_validate(updated_project)
        return None
        
    def update_project_visibility(self, project_id: uuid.UUID, visibility_data: ProjectVisibilityUpdate) -> Optional[ProjectResponse]:
        """Update a project's visibility"""
        logger.info(f"Updating visibility for project ID: {project_id}")
        
        # Get the project
        project = self.repository.get_by_id(project_id)
        if not project:
            logger.warning(f"Project with ID {project_id} not found")
            return None
        
        # Update visibility
        update_data = {"is_visible": visibility_data.is_visible}
        updated_project = self.repository.update(project_id, update_data)
        
        if updated_project:
            logger.info(f"Updated visibility for project ID {project_id} to {visibility_data.is_visible}")
            return ProjectResponse.model_validate(updated_project)
        
        return None

    def delete_project(self, project_id: uuid.UUID) -> bool:
        """Delete a project"""
        logger.info(f"Deleting project with ID: {project_id}")
        return self.repository.delete(project_id)
