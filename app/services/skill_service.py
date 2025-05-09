from app.models.skill_model import SkillGroup, Skill
from app.schemas.skill_schema import (
    SkillGroupCreate, SkillGroupUpdate, SkillGroupResponse,
    SkillGroupListResponse, SkillGroupVisibilityUpdate
)
from app.repositories.skill_repository import SkillGroupRepository
from app.models.skill_model import Skill
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
import uuid

logger = logging.getLogger(__name__)

class SkillGroupService:
    def __init__(self, db: Session):
        self.repository = SkillGroupRepository(db)
        
    def _convert_to_response_model(self, skill_group) -> SkillGroupResponse:
        """Convert SQLAlchemy model to Pydantic model"""
        # Convert skill_group to a dictionary format that Pydantic can validate
        if not skill_group:
            return None
            
        skill_group_dict = {
            "id": skill_group.id,
            "name": skill_group.name,
            "is_visible": skill_group.is_visible,
            "created_at": skill_group.created_at,
            "updated_at": skill_group.updated_at,
            "skills": [{
                "id": skill.id,
                "name": skill.name,
                "proficiency": skill.proficiency,
                "icon": skill.icon,
                "color": skill.color
            } for skill in skill_group.skills]
        }
        
        return SkillGroupResponse.model_validate(skill_group_dict)

    def create_skill_group(self, skill_group_data: SkillGroupCreate) -> SkillGroupResponse:
        """Create a new skill group"""
        logger.info(f"Creating skill group: {skill_group_data.name}")
        
        # Extract skills data first
        skills_data = skill_group_data.skills
        
        # Create skill group data without the skills
        skill_group_dict = {
            "name": skill_group_data.name,
            "is_visible": skill_group_data.is_visible
        }
        
        # Create the skill group without skills
        skill_group = self.repository.create(skill_group_dict)
        
        # Now create and add each skill to the group
        for skill_data in skills_data:
            # Convert Pydantic models to dictionaries
            skill_dict = skill_data.model_dump()
            # Add the skill group ID
            skill_dict["skill_group_id"] = skill_group.id
            # Add is_visible to match parent's visibility
            skill_dict["is_visible"] = skill_group.is_visible
            
            # Create the skill directly in the database
            new_skill = Skill(**skill_dict)
            self.repository.db.add(new_skill)
        
        # Commit the changes
        self.repository.db.commit()
        
        # Refresh to get the updated skill group with skills
        self.repository.db.refresh(skill_group)
        
        return self._convert_to_response_model(skill_group)

    def get_skill_groups(self, skip: int = 0, limit: int = 100, only_visible: bool = False) -> SkillGroupListResponse:
        """Get all skill groups, optionally filtering by visibility"""
        logger.info(f"Retrieving skill groups (skip={skip}, limit={limit}, only_visible={only_visible})")
        
        if only_visible:
            skill_groups = self.repository.get_visible(skip, limit)
            total = self.repository.count_visible()
        else:
            skill_groups = self.repository.get_all(skip, limit)
            total = self.repository.count()
            
        return SkillGroupListResponse(
            skill_groups=[self._convert_to_response_model(sg) for sg in skill_groups],
            total=total
        )
        
    def get_skill_group_by_id(self, skill_group_id: uuid.UUID, only_visible: bool = False) -> Optional[SkillGroupResponse]:
        """Get a skill group by ID, optionally filtering by visibility"""
        logger.info(f"Retrieving skill group with ID: {skill_group_id}, only_visible={only_visible}")
        
        if only_visible:
            skill_group = self.repository.get_visible_by_id(skill_group_id)
        else:
            skill_group = self.repository.get_by_id(skill_group_id)
            
        return self._convert_to_response_model(skill_group)

    def update_skill_group(self, skill_group_id: uuid.UUID, skill_group_data: SkillGroupUpdate) -> Optional[SkillGroupResponse]:
        """Update a skill group"""
        logger.info(f"Updating skill group with ID: {skill_group_id}")
        
        # Get the skill group to check if it exists
        skill_group = self.repository.get_by_id(skill_group_id)
        if not skill_group:
            logger.warning(f"Skill group with ID {skill_group_id} not found")
            return None
        
        # Convert to dict excluding unset fields
        update_dict = skill_group_data.model_dump(exclude_unset=True)
        
        # Check if skills are being updated
        if "skills" in update_dict:
            # Extract skills from the update dictionary
            skills_data = update_dict.pop("skills")
            
            # Remove existing skills
            for skill in skill_group.skills:
                self.repository.db.delete(skill)
            
            # Add new skills
            for skill_data in skills_data:
                # Convert Pydantic models to dictionaries if needed
                if hasattr(skill_data, "model_dump"):
                    skill_dict = skill_data.model_dump()
                else:
                    skill_dict = skill_data
                
                # Add the skill group ID
                skill_dict["skill_group_id"] = skill_group.id
                # Add is_visible to match parent's visibility
                skill_dict["is_visible"] = skill_group.is_visible
                
                # Create the skill
                new_skill = Skill(**skill_dict)
                self.repository.db.add(new_skill)
        
        # Update the skill group's own attributes
        for key, value in update_dict.items():
            setattr(skill_group, key, value)
        
        # Commit changes
        self.repository.db.commit()
        self.repository.db.refresh(skill_group)
        
        return self._convert_to_response_model(skill_group)

    def update_skill_group_visibility(self, skill_group_id: uuid.UUID, visibility_data: SkillGroupVisibilityUpdate) -> Optional[SkillGroupResponse]:
        """Update a skill group's visibility"""
        logger.info(f"Updating visibility for skill group ID: {skill_group_id}")
        
        # Get the skill group
        skill_group = self.repository.get_by_id(skill_group_id)
        if not skill_group:
            logger.warning(f"Skill group with ID {skill_group_id} not found")
            return None
        
        # Update visibility
        update_data = {"is_visible": visibility_data.is_visible}
        updated_skill_group = self.repository.update(skill_group_id, update_data)
        
        if updated_skill_group:
            logger.info(f"Updated visibility for skill group ID {skill_group_id} to {visibility_data.is_visible}")
            return self._convert_to_response_model(updated_skill_group)
        
        return None

    def delete_skill_group(self, skill_group_id: uuid.UUID) -> bool:
        """Delete a skill group"""
        logger.info(f"Deleting skill group with ID: {skill_group_id}")
        return self.repository.delete(skill_group_id)
