from sqlalchemy import Column, String, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
import uuid

class Skill(BaseModel):
    __tablename__ = "skills"
    
    name = Column(String(100), nullable=False, index=True)
    proficiency = Column(Integer, nullable=False)  # 1-5 rating
    color = Column(String(20), nullable=True)  # Color code for UI
    icon = Column(String(50), nullable=True)  # Icon name
    
    skill_group_id = Column(UUID(as_uuid=True), ForeignKey("skill_groups.id"), nullable=False)
    is_visible = Column(Boolean, default=True)  # Flag to control visibility

class SkillGroup(BaseModel):
    __tablename__ = "skill_groups"
    
    name = Column(String(100), nullable=False, index=True)  # Group name (e.g., "Frontend", "Backend", "DevOps")
    is_visible = Column(Boolean, default=True, nullable=False, server_default="true")  # Visibility flag
    
    # Relationship with skills
    skills = relationship("Skill", backref="skill_group", lazy="joined", cascade="all, delete-orphan")
