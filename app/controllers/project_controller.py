from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user_model import User
from app.services.project_service import ProjectService
from app.schemas.project_schema import (
    ProjectCreate, ProjectUpdate, ProjectResponse, 
    ProjectListResponse, ProjectVisibilityUpdate
)
from typing import Optional
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new project (requires authentication)"""
    service = ProjectService(db)
    return await service.create_project(project_data)

@router.get("", response_model=ProjectListResponse)
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all projects including hidden ones (requires authentication)"""
    service = ProjectService(db)
    return await service.get_projects(skip, limit, only_visible=False)

@router.get("/public", response_model=ProjectListResponse)
async def get_public_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get only visible projects (public endpoint, no authentication required)"""
    service = ProjectService(db)
    return await service.get_projects(skip, limit, only_visible=True)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single project by ID including if hidden (requires authentication)"""
    service = ProjectService(db)
    project = await service.get_project(project_id, only_visible=False)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    return project

# @router.get("/public/{project_id}", response_model=ProjectResponse)
# async def get_public_project(
#     project_id: uuid.UUID,
#     db: Session = Depends(get_db)
# ):
#     """Get a single visible project by ID (public endpoint, no authentication required)"""
#     service = ProjectService(db)
#     project = await service.get_project(project_id, only_visible=True)
#     if not project:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Project with ID {project_id} not found or not visible"
#         )
#     return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a project (requires authentication)"""
    service = ProjectService(db)
    updated_project = await service.update_project(project_id, project_data)
    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    return updated_project

@router.patch("/{project_id}/visibility", response_model=ProjectResponse)
def update_project_visibility(
    project_id: uuid.UUID,
    visibility_data: ProjectVisibilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a project's visibility (requires authentication)"""
    service = ProjectService(db)
    updated_project = service.update_project_visibility(project_id, visibility_data)
    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    return updated_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a project (requires authentication)"""
    service = ProjectService(db)
    result = service.delete_project(project_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )

@router.post("/{project_id}/refresh", response_model=ProjectResponse)
async def refresh_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Force refresh the GitHub data for a project (requires authentication).
    Only works for projects of type "github".
    """
    service = ProjectService(db)
    
    # Check if project exists
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    # Check if it's a GitHub project
    if project.type != "github":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only GitHub projects can be refreshed"
        )
    
    # Refresh the project
    refreshed_project = await service.refresh_github_data(project_id)
    if not refreshed_project:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh project data"
        )
    
    return refreshed_project
