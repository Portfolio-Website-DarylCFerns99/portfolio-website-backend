from sqlalchemy.orm import Session
from app.models.project_category_model import ProjectCategory
from app.repositories.base_repository import BaseRepository
from typing import List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
import logging
import uuid

logger = logging.getLogger(__name__)

class ProjectCategoryRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    @BaseRepository.retry_decorator
    def create(self, category_data: Dict[str, Any]) -> ProjectCategory:
        """Create a new project category with retry capability"""
        with self.transaction():
            category = ProjectCategory(**category_data)
            self.db.add(category)
        return category

    @BaseRepository.retry_decorator
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ProjectCategory]:
        """Get all categories with retry capability"""
        try:
            return self.db.query(ProjectCategory).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving project categories: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def get_visible(self, skip: int = 0, limit: int = 100) -> List[ProjectCategory]:
        """Get only visible categories with retry capability"""
        try:
            return self.db.query(ProjectCategory).filter(ProjectCategory.is_visible == True).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving visible project categories: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def get_by_id(self, category_id: uuid.UUID) -> Optional[ProjectCategory]:
        """Get a category by ID with retry capability"""
        try:
            return self.db.query(ProjectCategory).filter(ProjectCategory.id == category_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving project category {category_id}: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def get_visible_by_id(self, category_id: uuid.UUID) -> Optional[ProjectCategory]:
        """Get a visible category by ID with retry capability"""
        try:
            return self.db.query(ProjectCategory).filter(
                ProjectCategory.id == category_id,
                ProjectCategory.is_visible == True
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving visible project category {category_id}: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def count(self) -> int:
        """Count project categories with retry capability"""
        try:
            return self.db.query(ProjectCategory).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting project categories: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def count_visible(self) -> int:
        """Count visible project categories with retry capability"""
        try:
            return self.db.query(ProjectCategory).filter(ProjectCategory.is_visible == True).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting visible project categories: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def update(self, category_id: uuid.UUID, category_data: Dict[str, Any]) -> Optional[ProjectCategory]:
        """Update a project category with retry capability"""
        with self.transaction():
            category = self.get_by_id(category_id)
            if category:
                for key, value in category_data.items():
                    setattr(category, key, value)
        return category
