from sqlalchemy.orm import Session
from app.models.chat_model import ChatSession, ChatMessage
from app.repositories.base_repository import BaseRepository
import uuid

class ChatRepository(BaseRepository):
    def get_session(self, session_id: str):
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def get_or_create_session(self, session_id: str = None):
        if session_id:
            # Verify if it's a valid UUID
            try:
                uuid.UUID(str(session_id))
            except ValueError:
                session_id = None

        if session_id:
            # Check if exists
            existing_session = self.get_session(session_id)
            if existing_session:
                return existing_session
            
            # If not, create with this ID
            new_session = ChatSession(id=session_id)
        else:
            # Generate new
            new_session = ChatSession()

        try:
            self.db.add(new_session)
            self.safe_commit()
            return new_session
        except Exception as e:
            # Handle race condition or other errors
            self.db.rollback()
            # Try fetching again in case another request created it concurrently
            if session_id:
                existing = self.get_session(session_id)
                if existing:
                    return existing
            raise e

    def get_all_sessions(self, limit: int = 50, offset: int = 0):
        """
        Fetch all chat sessions with their latest message time and message count.
        """
        from sqlalchemy import func, desc
        
        # Subquery to get the last message time and count for each session
        subquery = self.db.query(
            ChatMessage.session_id,
            func.count(ChatMessage.id).label('message_count'),
            func.max(ChatMessage.created_at).label('last_message_at')
        ).group_by(ChatMessage.session_id).subquery()

        # Join ChatSession with the subquery
        query = self.db.query(ChatSession, subquery.c.message_count, subquery.c.last_message_at)\
            .outerjoin(subquery, ChatSession.id == subquery.c.session_id)\
            .order_by(desc(subquery.c.last_message_at))\
            .offset(offset)\
            .limit(limit)
            
        return query.all()

    def get_session_messages(self, session_id: str):
        """
        Fetch all messages for a specific session ordered by creation time.
        """
        return self.db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .order_by(ChatMessage.created_at.asc())\
            .all()

    def add_message(self, session_id: str, sender: str, content: str):
        # Ensure session exists before adding message
        self.get_or_create_session(session_id)
        
        message = ChatMessage(session_id=session_id, sender=sender, content=content)
        self.db.add(message)
        self.safe_commit()
        return message

    def get_recent_messages(self, session_id: str, limit: int = 50):
        return self.db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .order_by(ChatMessage.created_at.asc())\
            .all() # We want them in chronological order for the chat window
