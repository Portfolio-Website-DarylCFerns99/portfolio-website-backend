from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

# Base schema for shared attributes
class ReviewBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5, description="Rating must be between 1 and 5")
    where_known_from: Optional[str] = Field(None, max_length=200)
    is_visible: bool = False

# Schema for review creation
class ReviewCreate(ReviewBase):
    pass

# Schema for review update (only visibility flag can be updated)
class ReviewVisibilityUpdate(BaseModel):
    is_visible: bool

# Schema for review response (includes ID and timestamps)
class ReviewResponse(ReviewBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schema for review list response
class ReviewListResponse(BaseModel):
    reviews: List[ReviewResponse]
    total: int
