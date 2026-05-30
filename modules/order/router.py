from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.db.session import get_db
from modules.cart.repository import CartRepository
from modules.order.dto import CheckoutDTO, OrderDetailDTO, OrderDTO
from modules.order.repository import OrderRepository
from modules.order.use_cases import OrderUseCases

router = APIRouter()


def get_use_case(db: Session = Depends(get_db)) -> OrderUseCases:
    """Dependency that wires session, order repository, and cart repository."""
    return OrderUseCases(
        session=db,
        order_repo=OrderRepository(db),
        cart_repo=CartRepository(db),
    )


@router.get("/user/{user_id}", response_model=list[OrderDTO])
def list_user_orders(user_id: UUID, use_case: OrderUseCases = Depends(get_use_case)):
    """List all orders for a user."""
    return list(use_case.get_orders_by_user(user_id))


@router.get("/{order_id}", response_model=OrderDetailDTO)
def get_order(order_id: UUID, use_case: OrderUseCases = Depends(get_use_case)):
    """Get a full order with its items and payment details."""
    try:
        return use_case.get_order_detail(order_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/checkout/{user_id}", response_model=OrderDTO, status_code=status.HTTP_201_CREATED)
def checkout(
    user_id: UUID,
    dto: CheckoutDTO,
    use_case: OrderUseCases = Depends(get_use_case),
):
    """Convert the active cart into a confirmed order.

    Returns 409 if any item is out of stock, listing the affected products.
    The cart is marked as checked-out and stock is atomically decremented.
    """
    try:
        return use_case.checkout(user_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
