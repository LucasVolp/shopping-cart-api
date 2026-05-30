from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.payment import Payment


class PaymentRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_order_id(self, order_id: UUID) -> Payment | None:
        """Find the payment associated with a given order."""
        return self.session.scalars(
            select(Payment).where(Payment.order_id == order_id)
        ).first()

    def find_by_id(self, payment_id: UUID) -> Payment | None:
        """Find a payment by its own ID."""
        return self.session.scalars(
            select(Payment).where(Payment.id == payment_id)
        ).first()

    def update(self, payment: Payment) -> Payment:
        """Commit changes to an existing payment and return the refreshed instance."""
        self.session.commit()
        self.session.refresh(payment)
        return payment
