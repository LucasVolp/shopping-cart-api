from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models import Order


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_user_id(self, user_id: UUID) -> list[Order]:
        """Return all orders for a user, ordered by most recent first."""
        return list(
            self.session.scalars(
                select(Order)
                .where(Order.user_id == user_id)
                .order_by(Order.created_at.desc())
            ).all()
        )

    def find_by_id_with_details(self, order_id: UUID) -> Order | None:
        """Find an order by ID with items and payment eagerly loaded."""
        return self.session.scalars(
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.payment),
            )
            .where(Order.id == order_id)
        ).first()
