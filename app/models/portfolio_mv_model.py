from sqlalchemy import Column, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.config.database import Base

class PortfolioMV(Base):
    __tablename__ = 'portfolio_mv'

    # The view primary key is the user_id from the users table
    id = None # Override the BaseModel id if strictly needed, though SQLAlchemy usually requires a PK.
    user_id = Column(UUID(as_uuid=True), primary_key=True)

    name = Column(String(100), nullable=True)
    surname = Column(String(100), nullable=True)
    title = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    location = Column(String(100), nullable=True)
    availability = Column(String(50), nullable=True)
    avatar = Column(Text, nullable=True)
    social_links = Column(JSON, nullable=True)
    about = Column(JSON, nullable=True)
    featured_skill_ids = Column(JSON, nullable=True)

    # The aggregated JSON fields
    experiences = Column(JSON, nullable=True)
    projects = Column(JSON, nullable=True)
    skill_groups = Column(JSON, nullable=True)
    project_categories = Column(JSON, nullable=True)
    reviews = Column(JSON, nullable=True)
