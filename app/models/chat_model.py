from sqlalchemy import Column, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base_model import BaseModel

class ChatSession(BaseModel):
    __tablename__ = "chat_sessions"

    # UUID Primary Key 'id' is inherited from BaseModel
    # 'created_at' and 'updated_at' are inherited from BaseModel

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(BaseModel):
    __tablename__ = "chat_messages"

    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    sender = Column(String(50), nullable=False) # 'user' or 'bot'
    content = Column(Text, nullable=False)
    
    session = relationship("ChatSession", back_populates="messages")
