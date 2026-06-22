from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.db.session import get_db
from modules.cart.dto import AddCartItemDTO, CartDTO, UpdateCartItemDTO
from modules.cart.repository import CartRepository
from modules.cart.use_cases import CartUseCases

router = APIRouter()


def get_use_case(db: Session = Depends(get_db)) -> CartUseCases:
    """Dependency that wires the repository and use case for injection."""
    return CartUseCases(CartRepository(db))


@router.get("/{user_id}", response_model=CartDTO)
def get_cart(user_id: UUID, use_case: CartUseCases = Depends(get_use_case)):
    """Get the active cart for a user, creating one if it does not exist."""
    return use_case.get_cart(user_id)


@router.post("/{user_id}/items", response_model=CartDTO, status_code=status.HTTP_201_CREATED)
def add_item(
    user_id: UUID,
    dto: AddCartItemDTO,
    use_case: CartUseCases = Depends(get_use_case),
):
    """Add a product to the cart or increment its quantity if already present."""
    try:
        return use_case.add_item(user_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{user_id}/items/{item_id}", response_model=CartDTO)
def update_item(
    user_id: UUID,
    item_id: UUID,
    dto: UpdateCartItemDTO,
    use_case: CartUseCases = Depends(get_use_case),
):
    """Update the quantity of a specific cart item."""
    try:
        return use_case.update_item(user_id, item_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{user_id}/items/{item_id}", response_model=CartDTO)
def remove_item(
    user_id: UUID,
    item_id: UUID,
    use_case: CartUseCases = Depends(get_use_case),
):
    """Remove a specific item from the cart."""
    try:
        return use_case.remove_item(user_id, item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{user_id}/items", response_model=CartDTO)
def clear_cart(user_id: UUID, use_case: CartUseCases = Depends(get_use_case)):
    """Remove all items from the user's active cart."""
    return use_case.clear_cart(user_id)


@router.post("/{user_id}/undo", response_model=CartDTO)
def undo_last_action(user_id: UUID, use_case: CartUseCases = Depends(get_use_case)):
    """Undo the last cart action (add, update or remove) using the Stack data structure."""
    try:
        return use_case.undo_last_action(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
