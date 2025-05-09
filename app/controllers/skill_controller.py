from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user_model import User
from app.services.skill_service import SkillGroupService
from app.schemas.skill_schema import (
    SkillGroupCreate, SkillGroupUpdate, SkillGroupResponse,
    SkillGroupListResponse, SkillGroupVisibilityUpdate
)
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/skills",
    tags=["Skills"]
)

@router.post("/groups", response_model=SkillGroupResponse, status_code=status.HTTP_201_CREATED)
def create_skill_group(
    skill_group_data: SkillGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new skill group (requires authentication)"""
    service = SkillGroupService(db)
    return service.create_skill_group(skill_group_data)

@router.get("/groups", response_model=SkillGroupListResponse)
def get_skill_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all skill groups including hidden ones (requires authentication)"""
    service = SkillGroupService(db)
    return service.get_skill_groups(skip, limit, only_visible=False)

@router.get("/groups/public", response_model=SkillGroupListResponse)
def get_public_skill_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get only visible skill groups (public endpoint, no authentication required)"""
    service = SkillGroupService(db)
    return service.get_skill_groups(skip, limit, only_visible=True)

@router.get("/groups/{skill_group_id}", response_model=SkillGroupResponse)
def get_skill_group(
    skill_group_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a skill group by ID including if hidden (requires authentication)"""
    service = SkillGroupService(db)
    skill_group = service.get_skill_group_by_id(skill_group_id, only_visible=False)
    if not skill_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill group with ID {skill_group_id} not found"
        )
    return skill_group

@router.put("/groups/{skill_group_id}", response_model=SkillGroupResponse)
def update_skill_group(
    skill_group_id: uuid.UUID,
    skill_group_data: SkillGroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a skill group (requires authentication)"""
    service = SkillGroupService(db)
    updated_skill_group = service.update_skill_group(skill_group_id, skill_group_data)
    if not updated_skill_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill group with ID {skill_group_id} not found"
        )
    return updated_skill_group

@router.patch("/groups/{skill_group_id}/visibility", response_model=SkillGroupResponse)
def update_skill_group_visibility(
    skill_group_id: uuid.UUID,
    visibility_data: SkillGroupVisibilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a skill group's visibility (requires authentication)"""
    service = SkillGroupService(db)
    updated_skill_group = service.update_skill_group_visibility(skill_group_id, visibility_data)
    if not updated_skill_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill group with ID {skill_group_id} not found"
        )
    return updated_skill_group

@router.delete("/groups/{skill_group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill_group(
    skill_group_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a skill group (requires authentication)"""
    service = SkillGroupService(db)
    result = service.delete_skill_group(skill_group_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill group with ID {skill_group_id} not found"
        )
