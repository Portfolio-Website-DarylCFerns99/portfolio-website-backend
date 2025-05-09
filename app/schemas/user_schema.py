from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid

# Social link schema
class SocialLink(BaseModel):
    platform: str
    url: str
    tooltip: str
    icon: Optional[str] = None
    fileName: Optional[str] = None

# About section schema
class About(BaseModel):
    description: Optional[str] = None
    shortdescription: Optional[str] = None
    image: Optional[str] = Field(None, description="Base64 encoded image string")

# Base schema for shared required attributes
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

# Schema for user creation - only requires username, email, and password
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

# Schema for user update - includes optional profile fields
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    availability: Optional[str] = None
    avatar: Optional[str] = Field(None, description="Base64 encoded image string")
    social_links: Optional[List[SocialLink]] = None
    about: Optional[About] = None
    featured_skill_ids: Optional[List[uuid.UUID]] = Field(None, description="List of skill UUIDs to feature on profile")

# Schema for user response (excludes password)
class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    name: Optional[str] = None
    surname: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    availability: Optional[str] = None
    avatar: Optional[str] = Field(None, description="Base64 encoded image string")
    social_links: Optional[List[SocialLink]] = None
    about: Optional[About] = None
    featured_skill_ids: Optional[List[uuid.UUID]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        # Exclude hashed_password field from response
        exclude = {"hashed_password"}

# Schema for profile data
class UserProfile(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    availability: Optional[str] = None
    avatar: Optional[str] = Field(None, description="Base64 encoded image string")
    social_links: Optional[List[SocialLink]] = None
    about: Optional[About] = None
    featured_skill_ids: Optional[List[uuid.UUID]] = None

# Schema for token response
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
