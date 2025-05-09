from sqlalchemy.orm import Session
from app.models.review_model import Review
from app.repositories.base_repository import BaseRepository
from typing import List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
import logging
import uuid

logger = logging.getLogger(__name__)

class ReviewRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    @BaseRepository.retry_decorator
    def create(self, review_data: Dict[str, Any]) -> Review:
        """Create a new review with retry capability"""
        with self.transaction():
            review = Review(**review_data)
            self.db.add(review)
        return review

    @BaseRepository.retry_decorator
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Review]:
        """Get all reviews with retry capability"""
        try:
            return self.db.query(Review).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving reviews: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def get_visible(self, skip: int = 0, limit: int = 100) -> List[Review]:
        """Get only visible reviews with retry capability"""
        try:
            return self.db.query(Review).filter(Review.is_visible == True).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving visible reviews: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def get_by_id(self, review_id: uuid.UUID) -> Optional[Review]:
        """Get a review by ID with retry capability"""
        try:
            return self.db.query(Review).filter(Review.id == review_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving review {review_id}: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def update(self, review_id: uuid.UUID, review_data: Dict[str, Any]) -> Optional[Review]:
        """Update a review with retry capability"""
        with self.transaction():
            review = self.get_by_id(review_id)
            if review:
                for key, value in review_data.items():
                    setattr(review, key, value)
        return review

    @BaseRepository.retry_decorator
    def delete(self, review_id: uuid.UUID) -> bool:
        """Delete a review with retry capability"""
        with self.transaction():
            review = self.get_by_id(review_id)
            if review:
                self.db.delete(review)
                return True
            return False

    @BaseRepository.retry_decorator
    def count(self) -> int:
        """Count all reviews with retry capability"""
        try:
            return self.db.query(Review).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting reviews: {str(e)}")
            raise

    @BaseRepository.retry_decorator
    def count_visible(self) -> int:
        """Count visible reviews with retry capability"""
        try:
            return self.db.query(Review).filter(Review.is_visible == True).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting visible reviews: {str(e)}")
            raise
