from uuid import UUID

from sqlalchemy import update
from sqlalchemy.orm import Session

from core.data_structures.array import DynamicArray
from core.data_structures.linked_list import LinkedList
from models import Cart, CartItem, Order, OrderItem, Payment, Product
from models.enums.enums import CartStatus, OrderStatus, PaymentStatus
from modules.cart.repository import CartRepository
from modules.order.dto import CheckoutDTO
from modules.order.repository import OrderRepository


class OrderUseCases:
    def __init__(self, session: Session, order_repo: OrderRepository, cart_repo: CartRepository):
        self.session = session
        self.order_repo = order_repo
        self.cart_repo = cart_repo

    def get_orders_by_user(self, user_id: UUID) -> LinkedList[Order]:
        """Return all orders for a user loaded into a LinkedList.

        Uses the LinkedList data structure to store the purchase history.
        Complexity: O(n) — one append per order.
        """
        orders = self.order_repo.find_by_user_id(user_id)
        history: LinkedList[Order] = LinkedList()
        for order in orders:
            history.append(order)
        return history

    def get_order_detail(self, order_id: UUID) -> Order:
        """Return a single order with its items and payment or raise ValueError if not found."""
        order = self.order_repo.find_by_id_with_details(order_id)
        if not order:
            raise ValueError("Order not found")
        return order

    def checkout(self, user_id: UUID, dto: CheckoutDTO) -> Order:
        """Convert the active cart into a confirmed order.

        Race condition protection:
            Stock is decremented with a single atomic UPDATE per item:

                UPDATE product
                SET quantity_available = quantity_available - :qty
                WHERE id = :id AND quantity_available >= :qty

            If the WHERE clause fails (quantity_available < requested qty),
            rowcount == 0 and the item is added to the out-of-stock list.
            Because all operations share one database transaction and we only
            call session.commit() after every item succeeds, a partial failure
            automatically rolls back all previously decremented stock — no item
            is ever deducted from an order that was not fully fulfilled.

        Raises:
            ValueError: If the cart is empty, not found, or any item is out of stock.
                        The out-of-stock message lists the affected product names.
        """
        cart = self.cart_repo.find_active_by_user_id(user_id)
        if not cart or not cart.items:
            raise ValueError("Active cart is empty or not found")

        out_of_stock: list[str] = []
        total: float = 0.0
        snapshot: list[tuple[CartItem, float]] = []

        for item in cart.items:
            result = self.session.execute(
                update(Product)
                .where(
                    Product.id == item.product_id,
                    Product.quantity_available >= item.quantity,
                )
                .values(quantity_available=Product.quantity_available - item.quantity)
            )
            if result.rowcount == 0:
                out_of_stock.append(item.product.name)
            else:
                item_total = item.product.price * item.quantity
                total += item_total
                snapshot.append((item, item.product.price))

        if out_of_stock:
            self.session.rollback()
            raise ValueError(f"Out of stock: {', '.join(out_of_stock)}")

        order = Order(
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_amount=round(total, 2),
        )
        self.session.add(order)
        self.session.flush()

        for item, unit_price in snapshot:
            self.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    product_name=item.product.name,
                    unit_price=unit_price,
                    quantity=item.quantity,
                )
            )

        self.session.add(
            Payment(
                order_id=order.id,
                total_amount=round(total, 2),
                payment_status=PaymentStatus.PENDING,
                payment_method=dto.payment_method,
            )
        )

        cart.status = CartStatus.CHECKED_OUT

        self.session.commit()
        self.session.refresh(order)
        return order
