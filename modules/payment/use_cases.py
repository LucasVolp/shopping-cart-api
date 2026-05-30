from uuid import UUID

from models.payment import Payment
from modules.payment.dto import UpdatePaymentStatusDTO
from modules.payment.repository import PaymentRepository


class PaymentUseCases:
    def __init__(self, repository: PaymentRepository):
        self.repository = repository

    def get_by_order_id(self, order_id: UUID) -> Payment:
        """Return the payment for an order or raise ValueError if not found."""
        payment = self.repository.find_by_order_id(order_id)
        if not payment:
            raise ValueError("Payment not found for this order")
        return payment

    def update_status(self, payment_id: UUID, dto: UpdatePaymentStatusDTO) -> Payment:
        """Update the status of a payment.

        Intended for use by payment gateway webhooks or admin operations.
        Raises ValueError if the payment is not found.
        """
        payment = self.repository.find_by_id(payment_id)
        if not payment:
            raise ValueError("Payment not found")
        payment.payment_status = dto.payment_status
        return self.repository.update(payment)
