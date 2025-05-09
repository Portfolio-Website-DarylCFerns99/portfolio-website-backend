from sqlalchemy.orm import Session
from app.models.skill_model import SkillGroup
from app.repositories.base_repository import BaseRepository
from typing import List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
import logging
import uuid

logger = logging.getLogger(__name__)

class SkillGroupRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    @BaseRepository.retry_decorator
    def create(self, skill_group_data: Dict[str, Any]) -> SkillGroup:
        """Create a new skill group with retry capability"""
        with self.transaction():
            skill_group = SkillGroup(**skill_group_data)
            self.db.add(skill_group)
        return skill_group

    @BaseRepository.retry_decorator
    def get_all(self, skip: int = 0, limit: int = 100) -> List[SkillGroup]:
        """Get all skill groups with retry capability"""
        try:
            return self.db.query(SkillGroup).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving skill groups: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def get_visible(self, skip: int = 0, limit: int = 100) -> List[SkillGroup]:
        """Get only visible skill groups with retry capability"""
        try:
            return self.db.query(SkillGroup).filter(SkillGroup.is_visible == True).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving visible skill groups: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def get_by_id(self, skill_group_id: uuid.UUID) -> Optional[SkillGroup]:
        """Get a skill group by ID with retry capability"""
        try:
            return self.db.query(SkillGroup).filter(SkillGroup.id == skill_group_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving skill group {skill_group_id}: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def get_visible_by_id(self, skill_group_id: uuid.UUID) -> Optional[SkillGroup]:
        """Get a visible skill group by ID with retry capability"""
        try:
            return self.db.query(SkillGroup).filter(
                SkillGroup.id == skill_group_id,
                SkillGroup.is_visible == True
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving visible skill group {skill_group_id}: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def update(self, skill_group_id: uuid.UUID, skill_group_data: Dict[str, Any]) -> Optional[SkillGroup]:
        """Update a skill group with retry capability"""
        with self.transaction():
            skill_group = self.get_by_id(skill_group_id)
            if skill_group:
                for key, value in skill_group_data.items():
                    setattr(skill_group, key, value)
        return skill_group

    @BaseRepository.retry_decorator
    def delete(self, skill_group_id: uuid.UUID) -> bool:
        """Delete a skill group with retry capability"""
        with self.transaction():
            skill_group = self.get_by_id(skill_group_id)
            if skill_group:
                self.db.delete(skill_group)
                return True
            return False

    @BaseRepository.retry_decorator
    def count(self) -> int:
        """Count all skill groups with retry capability"""
        try:
            return self.db.query(SkillGroup).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting skill groups: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def count_visible(self) -> int:
        """Count visible skill groups with retry capability"""
        try:
            return self.db.query(SkillGroup).filter(SkillGroup.is_visible == True).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting visible skill groups: {str(e)}")
            raise
