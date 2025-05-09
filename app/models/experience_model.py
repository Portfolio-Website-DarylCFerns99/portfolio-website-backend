from sqlalchemy import Column, String, Text, Date, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.models.base_model import BaseModel
import uuid

class Experience(BaseModel):
    __tablename__ = "experiences"
    
    type = Column(String(50), nullable=False)  # 'experience' or 'education'
    title = Column(String(200), nullable=False)  # Job title or degree
    organization = Column(String(200), nullable=False)  # Company or institution
    start_date = Column(Date, nullable=False)  # Start date
    end_date = Column(Date, nullable=True)  # End date (nullable for current positions)
    description = Column(Text, nullable=True)  # Description
    is_visible = Column(Boolean, default=True)  # Flag to control visibility
