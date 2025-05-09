from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user_model import User
from app.services.experience_service import ExperienceService
from app.schemas.experience_schema import (
    ExperienceCreate, ExperienceUpdate, ExperienceResponse,
    ExperienceListResponse, ExperienceVisibilityUpdate
)
from typing import Optional
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/experiences",
    tags=["Experiences"]
)

@router.post("", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
def create_experience(
    experience_data: ExperienceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new experience or education entry (requires authentication)"""
    service = ExperienceService(db)
    return service.create_experience(experience_data)

@router.get("", response_model=ExperienceListResponse)
def get_experiences(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    type: Optional[str] = Query(None, description="Filter by type ('experience' or 'education')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all experiences and education entries including hidden ones (requires authentication)"""
    service = ExperienceService(db)
    
    if type:
        if type not in ["experience", "education"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Type must be either 'experience' or 'education'"
            )
        return service.get_experiences_by_type(type, skip, limit, only_visible=False)
    
    return service.get_experiences(skip, limit, only_visible=False)

@router.get("/public", response_model=ExperienceListResponse)
def get_public_experiences(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    type: Optional[str] = Query(None, description="Filter by type ('experience' or 'education')"),
    db: Session = Depends(get_db)
):
    """Get only visible experiences and education entries (public endpoint, no authentication required)"""
    service = ExperienceService(db)
    
    if type:
        if type not in ["experience", "education"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Type must be either 'experience' or 'education'"
            )
        return service.get_experiences_by_type(type, skip, limit, only_visible=True)
    
    return service.get_experiences(skip, limit, only_visible=True)

@router.get("/{experience_id}", response_model=ExperienceResponse)
def get_experience(
    experience_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get an experience or education entry by ID including if hidden (requires authentication)"""
    service = ExperienceService(db)
    experience = service.get_experience_by_id(experience_id, only_visible=False)
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experience with ID {experience_id} not found"
        )
    return experience

# @router.get("/public/{experience_id}", response_model=ExperienceResponse)
# def get_public_experience(
#     experience_id: uuid.UUID,
#     db: Session = Depends(get_db)
# ):
#     """Get a visible experience or education entry by ID (public endpoint, no authentication required)"""
#     service = ExperienceService(db)
#     experience = service.get_experience_by_id(experience_id, only_visible=True)
#     if not experience:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Experience with ID {experience_id} not found or not visible"
#         )
#     return experience

@router.put("/{experience_id}", response_model=ExperienceResponse)
def update_experience(
    experience_id: uuid.UUID,
    experience_data: ExperienceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an experience or education entry (requires authentication)"""
    service = ExperienceService(db)
    updated_experience = service.update_experience(experience_id, experience_data)
    if not updated_experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experience with ID {experience_id} not found"
        )
    return updated_experience

@router.patch("/{experience_id}/visibility", response_model=ExperienceResponse)
def update_experience_visibility(
    experience_id: uuid.UUID,
    visibility_data: ExperienceVisibilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an experience's visibility (requires authentication)"""
    service = ExperienceService(db)
    updated_experience = service.update_experience_visibility(experience_id, visibility_data)
    if not updated_experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experience with ID {experience_id} not found"
        )
    return updated_experience

@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(
    experience_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an experience or education entry (requires authentication)"""
    service = ExperienceService(db)
    result = service.delete_experience(experience_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experience with ID {experience_id} not found"
        )
