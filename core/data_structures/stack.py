from typing import Generic, Iterator, TypeVar

T = TypeVar("T")


class Stack(Generic[T]):
    """LIFO stack backed by a Python list.

    push/pop/peek are all O(1).
    """

    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        """Push an item onto the top of the stack. O(1)."""
        self._items.append(item)

    def pop(self) -> T:
        """Remove and return the top item. O(1). Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self) -> T:
        """Return the top item without removing it. O(1). Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(reversed(self._items))
