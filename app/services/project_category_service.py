from app.repositories.project_category_repository import ProjectCategoryRepository
from app.schemas.project_category_schema import ProjectCategoryResponse, ProjectCategoryListResponse, ProjectCategoryCreate, ProjectCategoryUpdate
from sqlalchemy.orm import Session
from typing import Optional
import logging
import uuid

logger = logging.getLogger(__name__)

class ProjectCategoryService:
    def __init__(self, db: Session):
        self.repository = ProjectCategoryRepository(db)

    def _to_response(self, category) -> Optional[ProjectCategoryResponse]:
        if not category:
            return None
        return ProjectCategoryResponse.model_validate(category)

    def get_categories(self, skip: int = 0, limit: int = 100, only_visible: bool = False) -> ProjectCategoryListResponse:
        logger.info(f"Retrieving project categories (skip={skip}, limit={limit}, only_visible={only_visible})")
        if only_visible:
            categories = self.repository.get_visible(skip, limit)
            total = self.repository.count_visible()
        else:
            categories = self.repository.get_all(skip, limit)
            total = self.repository.count()
        return ProjectCategoryListResponse(
            categories=[self._to_response(c) for c in categories],
            total=total
        )

    def get_category_by_id(self, category_id: uuid.UUID, only_visible: bool = False) -> Optional[ProjectCategoryResponse]:
        logger.info(f"Retrieving project category with ID: {category_id}, only_visible={only_visible}")
        if only_visible:
            category = self.repository.get_visible_by_id(category_id)
        else:
            category = self.repository.get_by_id(category_id)
        return self._to_response(category)

    def create_category(self, category_data: ProjectCategoryCreate) -> ProjectCategoryResponse:
        """Create a new project category"""
        logger.info(f"Creating project category: {category_data.name}")
        category_dict = category_data.model_dump()
        category = self.repository.create(category_dict)
        return self._to_response(category)

    def update_category(self, category_id: uuid.UUID, category_data: ProjectCategoryUpdate) -> Optional[ProjectCategoryResponse]:
        """Update a project category"""
        logger.info(f"Updating project category with ID: {category_id}")
        category = self.repository.get_by_id(category_id)
        if not category:
            return None
        update_dict = category_data.model_dump(exclude_unset=True)
        updated = self.repository.update(category_id, update_dict)
        if updated:
            return self._to_response(updated)
        return None
