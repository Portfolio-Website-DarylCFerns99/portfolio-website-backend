from typing import Generator
from sqlalchemy.orm import Session
from app.config.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    Creates a new database session for each request and closes it afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
