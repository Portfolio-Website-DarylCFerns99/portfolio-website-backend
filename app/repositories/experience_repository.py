from sqlalchemy.orm import Session
from app.models.experience_model import Experience
from app.repositories.base_repository import BaseRepository
from typing import List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
import logging
import uuid

logger = logging.getLogger(__name__)

class ExperienceRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    @BaseRepository.retry_decorator
    def create(self, experience_data: Dict[str, Any]) -> Experience:
        """Create a new experience with retry capability"""
        with self.transaction():
            experience = Experience(**experience_data)
            self.db.add(experience)
        return experience

    @BaseRepository.retry_decorator
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Experience]:
        """Get all experiences with retry capability"""
        try:
            return self.db.query(Experience).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving experiences: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def get_visible(self, skip: int = 0, limit: int = 100) -> List[Experience]:
        """Get only visible experiences with retry capability"""
        try:
            return self.db.query(Experience).filter(Experience.is_visible == True).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving visible experiences: {str(e)}")
            raise
            
    @BaseRepository.retry_decorator
    def get_by_type(self, type_: str, skip: int = 0, limit: int = 100, only_visible: bool = False) -> List[Experience]:
        """Get experiences filtered by type with retry capability"""
        try:
            query = self.db.query(Experience).filter(Experience.type == type_)
            if only_visible:
                query = query.filter(Experience.is_visible == True)
            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving {type_} experiences: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def get_by_id(self, experience_id: uuid.UUID) -> Optional[Experience]:
        """Get an experience by ID with retry capability"""
        try:
            return self.db.query(Experience).filter(Experience.id == experience_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving experience {experience_id}: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def get_visible_by_id(self, experience_id: uuid.UUID) -> Optional[Experience]:
        """Get a visible experience by ID with retry capability"""
        try:
            return self.db.query(Experience).filter(
                Experience.id == experience_id,
                Experience.is_visible == True
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving visible experience {experience_id}: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def update(self, experience_id: uuid.UUID, experience_data: Dict[str, Any]) -> Optional[Experience]:
        """Update an experience with retry capability"""
        with self.transaction():
            experience = self.get_by_id(experience_id)
            if experience:
                for key, value in experience_data.items():
                    setattr(experience, key, value)
        return experience

    @BaseRepository.retry_decorator
    def delete(self, experience_id: uuid.UUID) -> bool:
        """Delete an experience with retry capability"""
        with self.transaction():
            experience = self.get_by_id(experience_id)
            if experience:
                self.db.delete(experience)
                return True
            return False

    @BaseRepository.retry_decorator
    def count(self) -> int:
        """Count all experiences with retry capability"""
        try:
            return self.db.query(Experience).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting experiences: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def count_visible(self) -> int:
        """Count visible experiences with retry capability"""
        try:
            return self.db.query(Experience).filter(Experience.is_visible == True).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting visible experiences: {str(e)}")
            raise
            
    @BaseRepository.retry_decorator
    def count_by_type(self, type_: str, only_visible: bool = False) -> int:
        """Count experiences by type with retry capability"""
        try:
            query = self.db.query(Experience).filter(Experience.type == type_)
            if only_visible:
                query = query.filter(Experience.is_visible == True)
            return query.count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {type_} experiences: {str(e)}")
            raise
