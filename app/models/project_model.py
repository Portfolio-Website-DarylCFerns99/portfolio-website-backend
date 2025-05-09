from sqlalchemy import Column, String, Text, JSON, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.models.base_model import BaseModel
import uuid

class Project(BaseModel):
    __tablename__ = "projects"
    
    title = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)  # "github" or "custom"
    image = Column(Text, nullable=True)  # Base64 image data
    tags = Column(JSON, nullable=True)  # Store tags as a JSON array
    url = Column(String(255), nullable=True)
    additional_data = Column(JSON, nullable=True)  # Store complete GitHub API response
    expiry_date = Column(DateTime, nullable=True)  # Expiry date for non-custom projects
    is_visible = Column(Boolean, default=True)  # Flag to control visibility
