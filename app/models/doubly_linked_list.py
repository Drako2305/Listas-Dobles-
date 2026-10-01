from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, TypeVar


T = TypeVar("T")


@dataclass(slots=True, eq=False)
class Node(Generic[T]):
    value: T
    previous: Node[T] | None = None
    next: Node[T] | None = None


class DoublyLinkedList(Generic[T]):
    """A mutable sequence whose nodes link to both neighboring nodes."""

    def __init__(self) -> None:
        self.head: Node[T] | None = None
        self.tail: Node[T] | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        current = self.head
        while current is not None:
            yield current.value
            current = current.next

    def __reversed__(self) -> Iterator[T]:
        current = self.tail
        while current is not None:
            yield current.value
            current = current.previous

    def get_node(self, index: int) -> Node[T]:
        if index < 0 or index >= self._size:
            raise IndexError("List index out of range")

        if index < self._size // 2:
            current = self.head
            for _ in range(index):
                assert current is not None
                current = current.next
        else:
            current = self.tail
            for _ in range(self._size - index - 1):
                assert current is not None
                current = current.previous

        assert current is not None
        return current

    def insert(self, index: int, value: T) -> None:
        if index < 0 or index > self._size:
            raise IndexError("Insert index out of range")

        node = Node(value)
        if self._size == 0:
            self.head = self.tail = node
        elif index == 0:
            node.next = self.head
            assert self.head is not None
            self.head.previous = node
            self.head = node
        elif index == self._size:
            node.previous = self.tail
            assert self.tail is not None
            self.tail.next = node
            self.tail = node
        else:
            following = self.get_node(index)
            preceding = following.previous
            node.previous = preceding
            node.next = following
            following.previous = node
            assert preceding is not None
            preceding.next = node

        self._size += 1

    def append(self, value: T) -> None:
        self.insert(self._size, value)

    def remove(self, index: int) -> T:
        node = self.get_node(index)
        if node.previous is None:
            self.head = node.next
        else:
            node.previous.next = node.next

        if node.next is None:
            self.tail = node.previous
        else:
            node.next.previous = node.previous

        self._size -= 1
        node.previous = None
        node.next = None
        return node.value
