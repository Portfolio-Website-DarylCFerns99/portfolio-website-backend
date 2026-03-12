from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from contextlib import contextmanager
from app.utils.db_utils import get_retry_decorator
import logging

logger = logging.getLogger(__name__)

class BaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def _refresh_materialized_view(self):
        """Helper to safely refresh the portfolio_mv materialized view in the background and flush the RAM cache."""
        try:
            self.db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY portfolio_mv;"))
            self.db.commit()
            
            # Since the BaseRepository is generic, we don't naturally know which user owns the data being committed.
            # To be safe, we grab all users (typically just 1 in a portfolio) and flush their caches.
            from app.models.user_model import User
            from app.controllers.user_controller import clear_portfolio_cache
            
            users = self.db.query(User).all()
            for user in users:
                clear_portfolio_cache(user.id)
                
        except Exception as e:
            self.db.rollback()
            logger.warning(f"Could not refresh materialized view: {str(e)}")

    @contextmanager
    def transaction(self):
        """
        A context manager to handle database transactions with automatic rollback
        on exception and commit on success.
        """
        try:
            yield self.db
            self.db.commit()
            self._refresh_materialized_view()
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
            self._refresh_materialized_view()
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error during commit: {str(e)}")
            raise
