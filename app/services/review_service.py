from app.repositories.review_repository import ReviewRepository
from app.schemas.review_schema import ReviewCreate, ReviewResponse, ReviewListResponse, ReviewVisibilityUpdate
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import uuid

logger = logging.getLogger(__name__)

class ReviewService:
    def __init__(self, db: Session):
        self.repository = ReviewRepository(db)

    def create_review(self, review_data: ReviewCreate) -> ReviewResponse:
        """Create a new review"""
        logger.info(f"Creating review")
        
        # Convert to dict before passing to repository
        review_dict = review_data.model_dump()
        
        review = self.repository.create(review_dict)
        return ReviewResponse.model_validate(review)

    def get_reviews(self, skip: int = 0, limit: int = 100, only_visible: bool = False) -> ReviewListResponse:
        """Get reviews, optionally filtering by visibility"""
        logger.info(f"Retrieving reviews (skip={skip}, limit={limit}, only_visible={only_visible})")
        
        if only_visible:
            reviews = self.repository.get_visible(skip, limit)
            total = self.repository.count_visible()
        else:
            reviews = self.repository.get_all(skip, limit)
            total = self.repository.count()
            
        return ReviewListResponse(
            reviews=[ReviewResponse.model_validate(r) for r in reviews],
            total=total
        )
        
    def get_review_by_id(self, review_id: uuid.UUID) -> Optional[ReviewResponse]:
        """Get a review by ID regardless of visibility"""
        logger.info(f"Retrieving review with ID: {review_id}")
        review = self.repository.get_by_id(review_id)
        if review:
            return ReviewResponse.model_validate(review)
        return None

    def get_visible_review_by_id(self, review_id: uuid.UUID) -> Optional[ReviewResponse]:
        """Get a visible review by ID"""
        logger.info(f"Retrieving visible review with ID: {review_id}")
        review = self.repository.get_by_id(review_id)
        if review and review.is_visible:
            return ReviewResponse.model_validate(review)
        return None

    def update_review_visibility(self, review_id: uuid.UUID, visibility_data: ReviewVisibilityUpdate) -> Optional[ReviewResponse]:
        """Update a review's visibility"""
        logger.info(f"Updating visibility for review ID: {review_id}")
        
        # Get the review
        review = self.repository.get_by_id(review_id)
        if not review:
            logger.warning(f"Review with ID {review_id} not found")
            return None
        
        # Update visibility
        update_data = {"is_visible": visibility_data.is_visible}
        updated_review = self.repository.update(review_id, update_data)
        
        if updated_review:
            logger.info(f"Updated visibility for review ID {review_id} to {visibility_data.is_visible}")
            return ReviewResponse.model_validate(updated_review)
        
        return None

    def delete_review(self, review_id: uuid.UUID) -> bool:
        """Delete a review"""
        logger.info(f"Deleting review with ID: {review_id}")
        return self.repository.delete(review_id)
