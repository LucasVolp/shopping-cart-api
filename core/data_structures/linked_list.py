from typing import Generic, Iterator, Optional, TypeVar

T = TypeVar("T")


class _Node(Generic[T]):
    __slots__ = ("value", "next")

    def __init__(self, value: T) -> None:
        self.value = value
        self.next: Optional[_Node[T]] = None


class LinkedList(Generic[T]):
    """Singly linked list with O(1) append via a tail pointer.

    Supports iteration and len(). Use to_list() for a plain Python list.
    """

    def __init__(self) -> None:
        self._head: Optional[_Node[T]] = None
        self._tail: Optional[_Node[T]] = None
        self._length: int = 0

    def append(self, value: T) -> None:
        """Append a value to the tail. O(1)."""
        node = _Node(value)
        if self._tail is None:
            self._head = self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._length += 1

    def to_list(self) -> list[T]:
        """Return contents as a Python list. O(n)."""
        return list(self)

    def __iter__(self) -> Iterator[T]:
        current = self._head
        while current is not None:
            yield current.value
            current = current.next

    def __len__(self) -> int:
        return self._length
