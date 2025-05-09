from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from app.utils.db_utils import get_retry_decorator
import logging

logger = logging.getLogger(__name__)

class BaseRepository:
    def __init__(self, db: Session):
        self.db = db

    @contextmanager
    def transaction(self):
        """
        A context manager to handle database transactions with automatic rollback
        on exception and commit on success.
        """
        try:
            yield self.db
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Transaction rolled back due to error: {str(e)}")
            raise

    # The retry decorator wraps methods that need retry capability
    retry_decorator = get_retry_decorator()
    
    @retry_decorator
    def safe_commit(self):
        """Safely commit changes with retry capability"""
        try:
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error during commit: {str(e)}")
            raise
