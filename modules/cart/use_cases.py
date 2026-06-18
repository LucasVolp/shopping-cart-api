from typing import Any
from uuid import UUID

from core.data_structures.array import DynamicArray
from core.data_structures.stack import Stack
from models import Cart, CartItem
from models.enums.enums import CartStatus
from modules.cart.dto import AddCartItemDTO, UpdateCartItemDTO
from modules.cart.repository import CartRepository

# Per-user undo stacks keyed by user_id string.
# Each item is a dict describing the inverse of an add/update/remove operation.
_undo_stacks: dict[str, Stack[dict[str, Any]]] = {}


def _get_stack(user_id: UUID) -> Stack[dict[str, Any]]:
    key = str(user_id)
    if key not in _undo_stacks:
        _undo_stacks[key] = Stack()
    return _undo_stacks[key]


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

        Pushes an undo entry so the action can be reversed with undo_last_action().
        Raises ValueError if the product does not exist.
        """
        if not self.repository.find_product_by_id(dto.product_id):
            raise ValueError("Product not found")
        cart = self.get_cart(user_id)
        existing = self.repository.find_item_by_cart_and_product(cart.id, dto.product_id)
        if existing:
            prev_qty = existing.quantity
            existing.quantity += dto.quantity
            saved = self.repository.save_item(existing)
            _get_stack(user_id).push({
                "action": "ADD_EXISTING",
                "item_id": str(saved.id),
                "prev_quantity": prev_qty,
            })
        else:
            saved = self.repository.save_item(
                CartItem(cart_id=cart.id, product_id=dto.product_id, quantity=dto.quantity)
            )
            _get_stack(user_id).push({"action": "ADD_NEW", "item_id": str(saved.id)})
        return self.repository.find_active_by_user_id(user_id)

    def update_item(self, user_id: UUID, item_id: UUID, dto: UpdateCartItemDTO) -> Cart:
        """Update the quantity of a specific cart item.

        Pushes an undo entry so the previous quantity can be restored.
        Raises ValueError if the item does not exist or does not belong to the user's cart.
        """
        cart = self.get_cart(user_id)
        item = self.repository.find_item_by_id(item_id)
        if not item or item.cart_id != cart.id:
            raise ValueError("Cart item not found")
        prev_qty = item.quantity
        item.quantity = dto.quantity
        self.repository.save_item(item)
        _get_stack(user_id).push({
            "action": "UPDATE",
            "item_id": str(item_id),
            "prev_quantity": prev_qty,
        })
        return self.repository.find_active_by_user_id(user_id)

    def remove_item(self, user_id: UUID, item_id: UUID) -> Cart:
        """Remove a specific item from the cart.

        Pushes an undo entry so the item can be re-added with undo_last_action().
        Raises ValueError if the item does not exist or does not belong to the user's cart.
        """
        cart = self.get_cart(user_id)
        item = self.repository.find_item_by_id(item_id)
        if not item or item.cart_id != cart.id:
            raise ValueError("Cart item not found")
        _get_stack(user_id).push({
            "action": "REMOVE",
            "cart_id": str(cart.id),
            "product_id": str(item.product_id),
            "quantity": item.quantity,
        })
        self.repository.delete_item(item)
        return self.repository.find_active_by_user_id(user_id)

    def undo_last_action(self, user_id: UUID) -> Cart:
        """Reverse the most recent add, update, or remove operation for the user.

        Uses the Stack data structure (LIFO) to restore the previous cart state.
        Raises ValueError if there is nothing to undo.
        """
        stack = _get_stack(user_id)
        if stack.is_empty():
            raise ValueError("Nothing to undo")

        action = stack.pop()
        action_type = action["action"]

        if action_type == "ADD_NEW":
            item = self.repository.find_item_by_id(UUID(action["item_id"]))
            if item:
                self.repository.delete_item(item)

        elif action_type == "ADD_EXISTING":
            item = self.repository.find_item_by_id(UUID(action["item_id"]))
            if item:
                item.quantity = action["prev_quantity"]
                self.repository.save_item(item)

        elif action_type == "UPDATE":
            item = self.repository.find_item_by_id(UUID(action["item_id"]))
            if item:
                item.quantity = action["prev_quantity"]
                self.repository.save_item(item)

        elif action_type == "REMOVE":
            self.repository.save_item(
                CartItem(
                    cart_id=UUID(action["cart_id"]),
                    product_id=UUID(action["product_id"]),
                    quantity=action["quantity"],
                )
            )

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
