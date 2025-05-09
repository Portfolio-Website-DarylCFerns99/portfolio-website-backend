from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class Skill(BaseModel):
    id: Optional[uuid.UUID] = None
    name: str = Field(..., min_length=1, max_length=100)
    proficiency: Optional[int] = Field(None, ge=1, le=5, description="Optional proficiency level from 1-5")
    icon: Optional[str] = None
    color: Optional[str] = None

# Base schema for shared attributes
class SkillGroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    skills: List[Skill] = Field(..., min_items=1)
    is_visible: bool = True

# Schema for skill group creation
class SkillGroupCreate(SkillGroupBase):
    pass

# Schema for skill group update
class SkillGroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    skills: Optional[List[Skill]] = Field(None, min_items=1)
    is_visible: Optional[bool] = None

# Schema specifically for updating visibility
class SkillGroupVisibilityUpdate(BaseModel):
    is_visible: bool

# Schema for skill group response
class SkillGroupResponse(SkillGroupBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schema for skill group list response
class SkillGroupListResponse(BaseModel):
    skill_groups: List[SkillGroupResponse]
    total: int
