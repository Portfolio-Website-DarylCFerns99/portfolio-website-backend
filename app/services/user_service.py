from sqlalchemy.orm import Session
from app.models.user_model import User
from app.models.skill_model import Skill
from app.schemas.user_schema import UserUpdate
from typing import List, Optional
import logging
import uuid

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: Session):
        self.db = db
        
    def validate_featured_skills(self, user_id: uuid.UUID, skill_ids: List[uuid.UUID]) -> List[uuid.UUID]:
        """
        Validates that the provided skill IDs exist in the skills table.
        Returns only the valid skill IDs and discards any that don't exist.
        
        Args:
            user_id (uuid.UUID): The ID of the user
            skill_ids (List[uuid.UUID]): List of skill IDs to validate
            
        Returns:
            List[uuid.UUID]: List of valid skill IDs
        """
        if not skill_ids:
            return []
            
        logger.info(f"Validating {len(skill_ids)} featured skill IDs for user {user_id}")
        
        # Query the database to find which skill IDs exist
        existing_skills = self.db.query(Skill.id).filter(Skill.id.in_(skill_ids)).all()
        
        # Extract IDs from the query result
        valid_skill_ids = [str(skill.id) for skill in existing_skills]
        
        # Log information about discarded IDs
        discarded_ids = [str(id) for id in skill_ids if str(id) not in valid_skill_ids]
        if discarded_ids:
            logger.warning(f"Discarded {len(discarded_ids)} invalid skill IDs: {', '.join(discarded_ids)}")
        
        logger.info(f"Validated {len(valid_skill_ids)} skill IDs for user {user_id}")
        return valid_skill_ids
        
    def update_user_profile(self, user: User, user_data: UserUpdate) -> User:
        """
        Updates a user's profile with validated data.
        Validates featured skill IDs if they're included in the update.
        
        Args:
            user (User): The user model to update
            user_data (UserUpdate): The data to update the user with
            
        Returns:
            User: The updated user
        """
        # Convert to dict excluding unset fields
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Validate featured skill IDs if they're being updated
        if "featured_skill_ids" in update_data:
            feature_skill_ids = update_data["featured_skill_ids"]
            # Validate the skill IDs
            valid_skill_ids = self.validate_featured_skills(user.id, feature_skill_ids)
            # Update with only valid IDs
            update_data["featured_skill_ids"] = valid_skill_ids
        
        # Update user fields
        for key, value in update_data.items():
            setattr(user, key, value)
        
        # Save changes
        self.db.commit()
        self.db.refresh(user)
        
        return user
