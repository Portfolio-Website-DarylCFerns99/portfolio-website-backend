from app.repositories.experience_repository import ExperienceRepository
from app.schemas.experience_schema import (
    ExperienceCreate, ExperienceUpdate, ExperienceResponse,
    ExperienceListResponse, ExperienceVisibilityUpdate
)
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
import uuid

logger = logging.getLogger(__name__)

class ExperienceService:
    def __init__(self, db: Session):
        self.repository = ExperienceRepository(db)

    def create_experience(self, experience_data: ExperienceCreate) -> ExperienceResponse:
        """Create a new experience/education entry"""
        logger.info(f"Creating {experience_data.type} entry: {experience_data.title}")
        
        # Convert to dict before passing to repository
        experience_dict = experience_data.model_dump()
        
        experience = self.repository.create(experience_dict)
        return ExperienceResponse.model_validate(experience)

    def get_experiences(self, skip: int = 0, limit: int = 100, only_visible: bool = False) -> ExperienceListResponse:
        """Get all experiences, optionally filtering by visibility"""
        logger.info(f"Retrieving all experiences (skip={skip}, limit={limit}, only_visible={only_visible})")
        
        if only_visible:
            experiences = self.repository.get_visible(skip, limit)
            total = self.repository.count_visible()
        else:
            experiences = self.repository.get_all(skip, limit)
            total = self.repository.count()
            
        return ExperienceListResponse(
            experiences=[ExperienceResponse.model_validate(e) for e in experiences],
            total=total
        )
    
    def get_experiences_by_type(self, type_: str, skip: int = 0, limit: int = 100, only_visible: bool = False) -> ExperienceListResponse:
        """Get experiences filtered by type, optionally filtering by visibility"""
        logger.info(f"Retrieving {type_} entries (skip={skip}, limit={limit}, only_visible={only_visible})")
        
        experiences = self.repository.get_by_type(type_, skip, limit, only_visible)
        total = self.repository.count_by_type(type_, only_visible)
            
        return ExperienceListResponse(
            experiences=[ExperienceResponse.model_validate(e) for e in experiences],
            total=total
        )

    def get_experience_by_id(self, experience_id: uuid.UUID, only_visible: bool = False) -> Optional[ExperienceResponse]:
        """Get an experience by ID, optionally filtering by visibility"""
        logger.info(f"Retrieving experience with ID: {experience_id}, only_visible={only_visible}")
        
        if only_visible:
            experience = self.repository.get_visible_by_id(experience_id)
        else:
            experience = self.repository.get_by_id(experience_id)
            
        if experience:
            return ExperienceResponse.model_validate(experience)
        return None

    def update_experience(self, experience_id: uuid.UUID, experience_data: ExperienceUpdate) -> Optional[ExperienceResponse]:
        """Update an experience"""
        logger.info(f"Updating experience with ID: {experience_id}")
        
        # First get the experience to make sure it exists
        experience = self.repository.get_by_id(experience_id)
        if not experience:
            logger.warning(f"Experience with ID {experience_id} not found")
            return None
        
        # Convert to dict before passing to repository
        update_dict = experience_data.model_dump(exclude_unset=True)
        
        updated_experience = self.repository.update(experience_id, update_dict)
        if updated_experience:
            return ExperienceResponse.model_validate(updated_experience)
        return None

    def update_experience_visibility(self, experience_id: uuid.UUID, visibility_data: ExperienceVisibilityUpdate) -> Optional[ExperienceResponse]:
        """Update an experience's visibility"""
        logger.info(f"Updating visibility for experience ID: {experience_id}")
        
        # Get the experience
        experience = self.repository.get_by_id(experience_id)
        if not experience:
            logger.warning(f"Experience with ID {experience_id} not found")
            return None
        
        # Update visibility
        update_data = {"is_visible": visibility_data.is_visible}
        updated_experience = self.repository.update(experience_id, update_data)
        
        if updated_experience:
            logger.info(f"Updated visibility for experience ID {experience_id} to {visibility_data.is_visible}")
            return ExperienceResponse.model_validate(updated_experience)
        
        return None

    def delete_experience(self, experience_id: uuid.UUID) -> bool:
        """Delete an experience"""
        logger.info(f"Deleting experience with ID: {experience_id}")
        return self.repository.delete(experience_id)
