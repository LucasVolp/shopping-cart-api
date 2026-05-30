from uuid import UUID

from core.data_structures.array import DynamicArray
from models import Cart, CartItem
from models.enums.enums import CartStatus
from modules.cart.dto import AddCartItemDTO, UpdateCartItemDTO
from modules.cart.repository import CartRepository


class CartUseCases:
    def __init__(self, repository: CartRepository):
        self.repository = repository

    def get_cart(self, user_id: UUID) -> Cart:
        """Return the active cart for a user, creating one if it does not exist."""
        cart = self.repository.find_active_by_user_id(user_id)
        if not cart:
            cart = self.repository.create_cart(Cart(user_id=user_id, status=CartStatus.ACTIVE))
        return cart

    def add_item(self, user_id: UUID, dto: AddCartItemDTO) -> Cart:
        """Add a product to the cart or increment its quantity if already present.

        If the product is already in the cart, its quantity is incremented rather
        than creating a duplicate entry.
        """
        cart = self.get_cart(user_id)
        existing = self.repository.find_item_by_cart_and_product(cart.id, dto.product_id)
        if existing:
            existing.quantity += dto.quantity
            self.repository.save_item(existing)
        else:
            self.repository.save_item(
                CartItem(cart_id=cart.id, product_id=dto.product_id, quantity=dto.quantity)
            )
        return self.repository.find_active_by_user_id(user_id)

    def update_item(self, user_id: UUID, item_id: UUID, dto: UpdateCartItemDTO) -> Cart:
        """Update the quantity of a specific cart item.

        Raises ValueError if the item does not exist or does not belong to the user's cart.
        """
        cart = self.get_cart(user_id)
        item = self.repository.find_item_by_id(item_id)
        if not item or item.cart_id != cart.id:
            raise ValueError("Cart item not found")
        item.quantity = dto.quantity
        self.repository.save_item(item)
        return self.repository.find_active_by_user_id(user_id)

    def remove_item(self, user_id: UUID, item_id: UUID) -> Cart:
        """Remove a specific item from the cart.

        Raises ValueError if the item does not exist or does not belong to the user's cart.
        """
        cart = self.get_cart(user_id)
        item = self.repository.find_item_by_id(item_id)
        if not item or item.cart_id != cart.id:
            raise ValueError("Cart item not found")
        self.repository.delete_item(item)
        return self.repository.find_active_by_user_id(user_id)

    def clear_cart(self, user_id: UUID) -> Cart:
        """Remove all items from the user's active cart."""
        cart = self.get_cart(user_id)
        self.repository.clear_items(cart)
        return self.repository.find_active_by_user_id(user_id)

    def get_items_as_array(self, user_id: UUID) -> DynamicArray[CartItem]:
        """Return the cart items loaded into a DynamicArray.

        Complexity: O(n) — one append per item.
        """
        cart = self.get_cart(user_id)
        array: DynamicArray[CartItem] = DynamicArray()
        for item in cart.items:
            array.append(item)
        return array
