from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.db.session import get_db
from modules.category.dto import CategoryDTO, CreateCategoryDTO, UpdateCategoryDTO
from modules.category.repository import CategoryRepository
from modules.category.use_cases import CategoryUseCases

router = APIRouter()


def get_use_case(db: Session = Depends(get_db)) -> CategoryUseCases:
    """Dependency that wires the repository and use case for injection."""
    return CategoryUseCases(CategoryRepository(db))


@router.get("/", response_model=list[CategoryDTO])
def list_categories(use_case: CategoryUseCases = Depends(get_use_case)):
    """List all categories."""
    return list(use_case.get_all())


@router.get("/{category_id}", response_model=CategoryDTO)
def get_category(category_id: UUID, use_case: CategoryUseCases = Depends(get_use_case)):
    """Get a category by ID."""
    try:
        return use_case.get_by_id(category_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/", response_model=CategoryDTO, status_code=status.HTTP_201_CREATED)
def create_category(dto: CreateCategoryDTO, use_case: CategoryUseCases = Depends(get_use_case)):
    """Create a new category."""
    try:
        return use_case.create(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.put("/{category_id}", response_model=CategoryDTO)
def update_category(
    category_id: UUID,
    dto: UpdateCategoryDTO,
    use_case: CategoryUseCases = Depends(get_use_case),
):
    """Update a category's name."""
    try:
        return use_case.update(category_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: UUID, use_case: CategoryUseCases = Depends(get_use_case)):
    """Delete a category by ID."""
    try:
        use_case.delete(category_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
