from pydantic import BaseModel, Field, validator
from typing import Optional, List, Any, Dict
from datetime import datetime
import uuid

# Base schema for shared attributes
class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    type: str = Field(...) # "github" or "custom"
    image: Optional[str] = Field(None, description="Base64 encoded image string")
    tags: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    is_visible: bool = True  # Default to visible

    # Validate that type is either "github" or "custom"
    @validator('type')
    def validate_type(cls, v):
        if v not in ["github", "custom"]:
            raise ValueError('Type must be either "github" or "custom"')
        return v

# Schema for project creation
class ProjectCreate(ProjectBase):
    pass

# Schema for project update
class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    type: Optional[str] = None
    image: Optional[str] = Field(None, description="Base64 encoded image string")
    tags: Optional[List[str]] = None
    url: Optional[str] = None
    is_visible: Optional[bool] = None

    # Validate that type is either "github" or "custom" if provided
    @validator('type')
    def validate_type(cls, v):
        if v is not None and v not in ["github", "custom"]:
            raise ValueError('Type must be either "github" or "custom"')
        return v

# Schema specifically for updating visibility
class ProjectVisibilityUpdate(BaseModel):
    is_visible: bool

# Schema for project response with additional_data included
class ProjectResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    type: str
    image: Optional[str] = Field(None, description="Base64 encoded image string")
    tags: List[str] = []
    url: Optional[str] = None
    is_visible: bool
    additional_data: Optional[Dict[str, Any]] = None  # Include GitHub API response
    created_at: datetime
    updated_at: datetime
    expiry_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schema for project list response
class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
