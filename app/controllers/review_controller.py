from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user_model import User
from app.services.review_service import ReviewService
from app.schemas.review_schema import ReviewCreate, ReviewResponse, ReviewListResponse, ReviewVisibilityUpdate
from typing import Optional
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)

@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db)
):
    """Create a new review (requires authentication)"""
    service = ReviewService(db)
    return service.create_review(review_data)

@router.get("", response_model=ReviewListResponse)
def get_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all reviews including hidden ones (requires authentication)"""
    service = ReviewService(db)
    return service.get_reviews(skip, limit, only_visible=False)

@router.get("/public", response_model=ReviewListResponse)
def get_public_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get only visible reviews (public endpoint, no authentication required)"""
    service = ReviewService(db)
    return service.get_reviews(skip, limit, only_visible=True)

@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a review by ID including if hidden (requires authentication)"""
    service = ReviewService(db)
    review = service.get_review_by_id(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with ID {review_id} not found"
        )
    return review

# @router.get("/public/{review_id}", response_model=ReviewResponse)
# def get_public_review(
#     review_id: uuid.UUID,
#     db: Session = Depends(get_db)
# ):
#     """Get a visible review by ID (public endpoint, no authentication required)"""
#     service = ReviewService(db)
#     review = service.get_visible_review_by_id(review_id)
#     if not review:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Review with ID {review_id} not found or not visible"
#         )
#     return review

@router.patch("/{review_id}/visibility", response_model=ReviewResponse)
def update_review_visibility(
    review_id: uuid.UUID,
    visibility_data: ReviewVisibilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a review's visibility (requires authentication)"""
    service = ReviewService(db)
    updated_review = service.update_review_visibility(review_id, visibility_data)
    if not updated_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with ID {review_id} not found"
        )
    return updated_review

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a review (requires authentication)"""
    service = ReviewService(db)
    result = service.delete_review(review_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with ID {review_id} not found"
        )
