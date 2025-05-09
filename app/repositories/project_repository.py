from sqlalchemy.orm import Session
from app.models.project_model import Project
from app.repositories.base_repository import BaseRepository
from typing import List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
import logging
import uuid

logger = logging.getLogger(__name__)

class ProjectRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    @BaseRepository.retry_decorator
    def create(self, project_data: Dict[str, Any]) -> Project:
        """Create a new project with retry capability"""
        with self.transaction():
            project = Project(**project_data)
            self.db.add(project)
        return project

    @BaseRepository.retry_decorator
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get all projects with retry capability"""
        try:
            return self.db.query(Project).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving projects: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def get_visible(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get only visible projects with retry capability"""
        try:
            return self.db.query(Project).filter(Project.is_visible == True).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving visible projects: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def get_by_id(self, project_id: uuid.UUID) -> Optional[Project]:
        """Get a project by ID with retry capability"""
        try:
            return self.db.query(Project).filter(Project.id == project_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving project {project_id}: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def get_visible_by_id(self, project_id: uuid.UUID) -> Optional[Project]:
        """Get a visible project by ID with retry capability"""
        try:
            return self.db.query(Project).filter(
                Project.id == project_id,
                Project.is_visible == True
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving visible project {project_id}: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def update(self, project_id: uuid.UUID, project_data: Dict[str, Any]) -> Optional[Project]:
        """Update a project with retry capability"""
        with self.transaction():
            project = self.get_by_id(project_id)
            if project:
                for key, value in project_data.items():
                    setattr(project, key, value)
        return project

    @BaseRepository.retry_decorator
    def delete(self, project_id: uuid.UUID) -> bool:
        """Delete a project with retry capability"""
        with self.transaction():
            project = self.get_by_id(project_id)
            if project:
                self.db.delete(project)
                return True
            return False

    @BaseRepository.retry_decorator
    def count(self) -> int:
        """Count projects with retry capability"""
        try:
            return self.db.query(Project).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting projects: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def count_visible(self) -> int:
        """Count visible projects with retry capability"""
        try:
            return self.db.query(Project).filter(Project.is_visible == True).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting visible projects: {str(e)}")
            raise
