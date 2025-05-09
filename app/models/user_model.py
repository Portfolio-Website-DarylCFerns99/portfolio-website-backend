from sqlalchemy import Column, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.models.base_model import BaseModel
from app.models.skill_model import Skill

class User(BaseModel):
    __tablename__ = "users"
    
    # Required fields
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Optional fields
    name = Column(String(100), nullable=True)
    surname = Column(String(100), nullable=True)
    title = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    location = Column(String(100), nullable=True)
    availability = Column(String(50), nullable=True)
    avatar = Column(Text, nullable=True)
    social_links = Column(JSON, nullable=True)
    about = Column(JSON, nullable=True)
    featured_skill_ids = Column(JSON, nullable=True, default=list)
