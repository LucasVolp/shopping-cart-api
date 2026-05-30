from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.db.session import get_db
from modules.user.dto import CreateUserDTO, UpdateUserDTO, UserDTO, UserDetailDTO
from modules.user.repository import UserRepository
from modules.user.use_cases import UserUseCases

router = APIRouter()


def get_use_case(db: Session = Depends(get_db)) -> UserUseCases:
    """Dependency that wires the repository and use case for injection."""
    return UserUseCases(UserRepository(db))


@router.get("/", response_model=list[UserDTO])
def list_users(use_case: UserUseCases = Depends(get_use_case)):
    """List all registered users."""
    return use_case.get_all()


@router.get("/{user_id}", response_model=UserDTO)
def get_user(user_id: UUID, use_case: UserUseCases = Depends(get_use_case)):
    """Get a user by ID."""
    try:
        return use_case.get_by_id(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{user_id}/details", response_model=UserDetailDTO)
def get_user_details(user_id: UUID, use_case: UserUseCases = Depends(get_use_case)):
    """Get a user with their full order history."""
    try:
        return use_case.get_by_id_with_orders(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
def create_user(dto: CreateUserDTO, use_case: UserUseCases = Depends(get_use_case)):
    """Create a new user."""
    try:
        return use_case.create(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.put("/{user_id}", response_model=UserDTO)
def update_user(
    user_id: UUID,
    dto: UpdateUserDTO,
    use_case: UserUseCases = Depends(get_use_case),
):
    """Update a user's name or email."""
    try:
        return use_case.update(user_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, use_case: UserUseCases = Depends(get_use_case)):
    """Delete a user by ID."""
    try:
        use_case.delete(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
