from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import uuid


class ProjectCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    is_visible: bool = True

class ProjectCategoryCreate(ProjectCategoryBase):
    pass

class ProjectCategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    is_visible: bool | None = None


class ProjectCategoryResponse(ProjectCategoryBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectCategoryListResponse(BaseModel):
    categories: List[ProjectCategoryResponse]
    total: int
