from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models import Cart, CartItem
from models.enums.enums import CartStatus


class CartRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_active_by_user_id(self, user_id: UUID) -> Cart | None:
        """Find the active cart for a user, eagerly loading items and their products."""
        return self.session.scalars(
            select(Cart)
            .options(selectinload(Cart.items).selectinload(CartItem.product))
            .where(Cart.user_id == user_id, Cart.status == CartStatus.ACTIVE)
        ).first()

    def find_item_by_id(self, item_id: UUID) -> CartItem | None:
        """Find a cart item by ID."""
        return self.session.scalars(
            select(CartItem).where(CartItem.id == item_id)
        ).first()

    def find_item_by_cart_and_product(self, cart_id: UUID, product_id: UUID) -> CartItem | None:
        """Find an existing item in a cart for a specific product."""
        return self.session.scalars(
            select(CartItem).where(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id,
            )
        ).first()

    def create_cart(self, cart: Cart) -> Cart:
        """Persist a new cart and return it with generated fields populated."""
        self.session.add(cart)
        self.session.commit()
        self.session.refresh(cart)
        return cart

    def save_item(self, item: CartItem) -> CartItem:
        """Persist a new or updated cart item."""
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def delete_item(self, item: CartItem) -> None:
        """Remove an item from the cart."""
        self.session.delete(item)
        self.session.commit()

    def clear_items(self, cart: Cart) -> None:
        """Remove all items from a cart."""
        for item in cart.items:
            self.session.delete(item)
        self.session.commit()
