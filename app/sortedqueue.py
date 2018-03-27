# coding=utf-8
# Project available at https://github.com/denexapp/advanced-status-vk
from typing import Callable, TypeVar, Generic

T = TypeVar('T')


class SortedQueue(Generic[T]):
    def __init__(self, key: Callable[[T], float]):
        self._next = None
        self._count = 0
        self._get_key = key

    def append(self, item: T):
        item_key = self._get_key(item)
        node = self
        while node._next is not None:
            if node._next.key <= item_key:
                node = node._next
            else:
                break
        node._next = self._Node(item, self._get_key(item), node._next)
        self._count += 1

    def pop(self) -> T:
        if self._count == 0:
            raise Exception("There are no items in the queue")
        result = self._next
        self._next = result._next
        self._count -= 1
        return result.item

    def get_head(self) -> T:
        return self._next.item if self._next is not None else None

    def __len__(self):
        return self._count

    class _Node(Generic[T]):
        def __init__(self, item: T, key: float, next_node: 'SortedQueue._Node' = None):
            self.item = item
            self._next = next_node
            self.key = key
