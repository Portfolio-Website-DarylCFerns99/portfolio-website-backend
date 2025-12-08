from sqlalchemy import Column, String, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from app.models.base_model import BaseModel
import uuid

class VectorEmbedding(BaseModel):
    __tablename__ = "vector_embeddings"
    
    # Content that was embedded (the "chunk" of text)
    content = Column(Text, nullable=False)
    
    # The Vector itself (768 dimensions is standard for Gemini-1.5-Flash / text-embedding-004)
    # Note: text-embedding-004 output dimension is 768.
    embedding = Column(Vector(768), nullable=False)
    
    # Metadata for filtering and context (e.g. source_type='project', source_id='...')
    metadata_json = Column(JSON, nullable=True)
    
    # What type of data is this? (project, skill, experience, review, user)
    source_type = Column(String(50), nullable=False, index=True)
    
    # ID of the original record (if applicable)
    source_id = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self):
        return f"<VectorEmbedding(id={self.id}, source={self.source_type})>"
