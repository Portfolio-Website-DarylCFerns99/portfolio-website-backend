from sqlalchemy import Column, String, Boolean
from app.models.base_model import BaseModel


class ProjectCategory(BaseModel):
    __tablename__ = "project_categories"

    name = Column(String(100), nullable=False, index=True)
    is_visible = Column(Boolean, default=True, nullable=False, server_default="true")
