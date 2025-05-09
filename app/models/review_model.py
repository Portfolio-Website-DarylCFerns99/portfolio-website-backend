from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.models.base_model import BaseModel
import uuid

class Review(BaseModel):
    __tablename__ = "reviews"
    
    name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    rating = Column(String(10), nullable=False)
    where_known_from = Column(String(200), nullable=True)
    is_visible = Column(Boolean, default=True)  # Flag to control visibility
