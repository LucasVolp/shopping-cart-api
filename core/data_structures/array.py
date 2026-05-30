import ctypes
from typing import Generic, Iterator, TypeVar

T = TypeVar("T")


class DynamicArray(Generic[T]):
    """A generic dynamic array backed by a fixed C-level array.

    Doubles its capacity whenever the internal buffer is full,
    mimicking the growth strategy of ArrayList (Java) and std::vector (C++).

    Complexity summary:
        append   — O(1) amortized  (occasional O(n) resize)
        get      — O(1)
        remove   — O(n)
        __len__  — O(1)
        __iter__ — O(n)
    """

    def __init__(self, capacity: int = 4) -> None:
        """Initialise the array with a fixed internal buffer.

        Args:
            capacity: Initial number of slots allocated in memory.
        """
        self._length = 0
        self._capacity = capacity
        self._data = self._make_array(self._capacity)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def append(self, item: T) -> None:
        """Add an item to the end of the array.

        When the buffer is full a resize is triggered, allocating a new
        buffer with double the current capacity and copying every existing
        element — O(n) work that happens at most once every n appends,
        giving O(1) amortised cost overall.

        Args:
            item: The element to add.

        Complexity: O(1) amortized — O(n) only on resize.
        """
        if self._length == self._capacity:
            self._resize(2 * self._capacity)
        self._data[self._length] = item
        self._length += 1

    def get(self, index: int) -> T:
        """Return the element at the given index.

        Because the backing store is a contiguous block of memory, the
        address of position i is computed directly as:
            base_address + i * element_size
        No traversal is needed — the lookup is always one step.

        Args:
            index: Zero-based position to retrieve.

        Returns:
            The element stored at that position.

        Raises:
            IndexError: If index is out of bounds.

        Complexity: O(1) — direct memory address calculation.
        """
        if not 0 <= index < self._length:
            raise IndexError(f"Index {index} out of range for length {self._length}")
        return self._data[index]

    def remove(self, index: int) -> None:
        """Remove the element at the given index, shifting subsequent elements left.

        Every element after the removed position must move one slot to the
        left to keep the array contiguous.  In the worst case (index 0) all
        n elements are shifted — O(n).

        Args:
            index: Zero-based position to remove.

        Raises:
            IndexError: If index is out of bounds.

        Complexity: O(n) — up to n shifts in the worst case.
        """
        if not 0 <= index < self._length:
            raise IndexError(f"Index {index} out of range for length {self._length}")
        for i in range(index, self._length - 1):
            self._data[i] = self._data[i + 1]
        self._data[self._length - 1] = None
        self._length -= 1

    def to_list(self) -> list[T]:
        """Return a plain Python list with all current elements.

        Complexity: O(n).
        """
        return [self._data[i] for i in range(self._length)]

    # ------------------------------------------------------------------
    # Python protocol methods
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of elements currently stored.

        Complexity: O(1) — length is tracked as a counter.
        """
        return self._length

    def __getitem__(self, index: int) -> T:
        """Support bracket notation: array[i].

        Complexity: O(1).
        """
        return self.get(index)

    def __iter__(self) -> Iterator[T]:
        """Allow iteration with for-loops and list().

        Complexity: O(n).
        """
        for i in range(self._length):
            yield self._data[i]

    def __repr__(self) -> str:
        items = ", ".join(repr(self._data[i]) for i in range(self._length))
        return f"DynamicArray([{items}]) length={self._length} capacity={self._capacity}"

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _resize(self, new_capacity: int) -> None:
        """Allocate a new buffer of new_capacity and copy all elements into it.

        This is the core cost of the dynamic array: a full O(n) copy triggered
        whenever the buffer is exhausted.  By doubling the capacity each time,
        the total copy work across all appends stays proportional to n, which
        is why the amortised per-append cost remains O(1).

        Args:
            new_capacity: Size of the replacement buffer.

        Complexity: O(n).
        """
        new_data = self._make_array(new_capacity)
        for i in range(self._length):
            new_data[i] = self._data[i]
        self._data = new_data
        self._capacity = new_capacity

    @staticmethod
    def _make_array(capacity: int) -> ctypes.Array:
        """Allocate a fixed-size C-level array of Python object references.

        Unlike a Python list, this buffer cannot grow on its own — it is a
        raw block of memory slots, which is exactly what a real array is.

        Args:
            capacity: Number of slots to allocate.

        Returns:
            A fixed ctypes array of py_object with the given capacity.
        """
        return (capacity * ctypes.py_object)()
