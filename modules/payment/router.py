from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.db.session import get_db
from modules.payment.dto import PaymentDTO, UpdatePaymentStatusDTO
from modules.payment.repository import PaymentRepository
from modules.payment.use_cases import PaymentUseCases

router = APIRouter()


def get_use_case(db: Session = Depends(get_db)) -> PaymentUseCases:
    """Dependency that wires the repository and use case for injection."""
    return PaymentUseCases(PaymentRepository(db))


@router.get("/order/{order_id}", response_model=PaymentDTO)
def get_payment_by_order(order_id: UUID, use_case: PaymentUseCases = Depends(get_use_case)):
    """Get the payment associated with an order."""
    try:
        return use_case.get_by_order_id(order_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{payment_id}/status", response_model=PaymentDTO)
def update_payment_status(
    payment_id: UUID,
    dto: UpdatePaymentStatusDTO,
    use_case: PaymentUseCases = Depends(get_use_case),
):
    """Update the status of a payment (webhook or admin use)."""
    try:
        return use_case.update_status(payment_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
