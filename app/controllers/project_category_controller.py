from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user_model import User
from app.services.project_category_service import ProjectCategoryService
from app.schemas.project_category_schema import (
    ProjectCategoryResponse,
    ProjectCategoryListResponse,
    ProjectCategoryUpdate,
    ProjectCategoryCreate
)
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/project-categories",
    tags=["Project Categories"]
)

@router.post("", response_model=ProjectCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: ProjectCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new project category (requires authentication)"""
    service = ProjectCategoryService(db)
    return service.create_category(category_data)

@router.get("", response_model=ProjectCategoryListResponse)
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all project categories including hidden ones (requires authentication)"""
    service = ProjectCategoryService(db)
    return service.get_categories(skip, limit, only_visible=False)

@router.get("/public", response_model=ProjectCategoryListResponse)
def get_public_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get only visible project categories (public endpoint, no authentication required)"""
    service = ProjectCategoryService(db)
    return service.get_categories(skip, limit, only_visible=True)

@router.get("/{category_id}", response_model=ProjectCategoryResponse)
def get_category(
    category_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a project category by ID including if hidden (requires authentication)"""
    service = ProjectCategoryService(db)
    category = service.get_category_by_id(category_id, only_visible=False)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project category with ID {category_id} not found"
        )
    return category

@router.put("/{category_id}", response_model=ProjectCategoryResponse)
def update_category(
    category_id: uuid.UUID,
    category_data: ProjectCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a project category (requires authentication)"""
    service = ProjectCategoryService(db)
    updated = service.update_category(category_id, category_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project category with ID {category_id} not found"
        )
    return updated
