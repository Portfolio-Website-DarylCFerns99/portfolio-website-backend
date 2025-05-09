from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def get_retry_decorator():
    """
    Creates a retry decorator with the configured settings.
    Used to retry database operations in case of temporary failures.
    """
    return retry(
        stop=stop_after_attempt(settings.MAX_DB_RETRIES),
        wait=wait_exponential(multiplier=settings.RETRY_BACKOFF),
        retry=retry_if_db_error,
        before_sleep=log_retry_attempt,
    )

def retry_if_db_error(exception):
    """Check if the exception is a database error that should be retried."""
    retry_errors = (OperationalError,)
    should_retry = isinstance(exception, retry_errors)
    
    # Don't retry specific errors like unique constraint violations
    if isinstance(exception, SQLAlchemyError) and not should_retry:
        if isinstance(exception, IntegrityError):
            return False
    
    return should_retry

def log_retry_attempt(retry_state):
    """Log information about the retry attempt."""
    exception = retry_state.outcome.exception()
    logger.warning(
        f"Retrying database operation: attempt {retry_state.attempt_number} after error: {str(exception)}"
    )
