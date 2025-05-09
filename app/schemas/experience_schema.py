from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
import uuid

# Base schema for shared attributes
class ExperienceBase(BaseModel):
    type: str = Field(..., description="Type of entry ('experience' or 'education')")
    title: str = Field(..., min_length=1, max_length=200, description="Job title or degree")
    organization: str = Field(..., min_length=1, max_length=200, description="Company or institution")
    start_date: date = Field(..., description="Start date")
    end_date: Optional[date] = Field(None, description="End date (null for current positions)")
    description: Optional[str] = Field(None, description="Description of the experience or education")
    is_visible: bool = Field(True, description="Whether the entry is visible publicly")

    # Validate that type is either "experience" or "education"
    @validator('type')
    def validate_type(cls, v):
        if v not in ["experience", "education"]:
            raise ValueError('Type must be either "experience" or "education"')
        return v
    
    # Validate that end_date is after start_date if provided
    @validator('end_date')
    def validate_dates(cls, v, values):
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v

# Schema for experience creation
class ExperienceCreate(ExperienceBase):
    pass

# Schema for experience update
class ExperienceUpdate(BaseModel):
    type: Optional[str] = Field(None, description="Type of entry ('experience' or 'education')")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Job title or degree")
    organization: Optional[str] = Field(None, min_length=1, max_length=200, description="Company or institution")
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date (null for current positions)")
    description: Optional[str] = Field(None, description="Description of the experience or education")
    is_visible: Optional[bool] = Field(None, description="Whether the entry is visible publicly")

    # Validate that type is either "experience" or "education" if provided
    @validator('type')
    def validate_type(cls, v):
        if v is not None and v not in ["experience", "education"]:
            raise ValueError('Type must be either "experience" or "education"')
        return v
    
    # Validate that end_date is after start_date if both are provided
    @validator('end_date')
    def validate_dates(cls, v, values):
        if v and 'start_date' in values and values['start_date'] and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v

# Schema specifically for updating visibility
class ExperienceVisibilityUpdate(BaseModel):
    is_visible: bool

# Schema for experience response
class ExperienceResponse(BaseModel):
    id: uuid.UUID
    type: str
    title: str
    organization: str
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None
    is_visible: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schema for experience list response
class ExperienceListResponse(BaseModel):
    experiences: List[ExperienceResponse]
    total: int
