import unittest

from app.models.doubly_linked_list import DoublyLinkedList


class DoublyLinkedListTests(unittest.TestCase):
    def test_empty_list_has_no_endpoints(self) -> None:
        linked_list: DoublyLinkedList[int] = DoublyLinkedList()
        self.assertEqual(len(linked_list), 0)
        self.assertIsNone(linked_list.head)
        self.assertIsNone(linked_list.tail)
        self.assertEqual(list(linked_list), [])
        self.assertEqual(list(reversed(linked_list)), [])

    def test_insert_and_traverse_in_both_directions(self) -> None:
        linked_list: DoublyLinkedList[str] = DoublyLinkedList()
        linked_list.append("second")
        linked_list.insert(0, "first")
        linked_list.insert(2, "fourth")
        linked_list.insert(2, "third")

        self.assertEqual(list(linked_list), ["first", "second", "third", "fourth"])
        self.assertEqual(list(reversed(linked_list)), ["fourth", "third", "second", "first"])
        self.assertEqual(linked_list.head.value, "first")
        self.assertEqual(linked_list.tail.value, "fourth")
        self.assertIs(linked_list.head.next.previous, linked_list.head)
        self.assertIs(linked_list.tail.previous.next, linked_list.tail)

    def test_remove_head_middle_tail_and_last_node(self) -> None:
        linked_list: DoublyLinkedList[int] = DoublyLinkedList()
        for value in range(4):
            linked_list.append(value)

        self.assertEqual(linked_list.remove(0), 0)
        self.assertEqual(linked_list.remove(1), 2)
        self.assertEqual(linked_list.remove(1), 3)
        self.assertEqual(linked_list.remove(0), 1)
        self.assertEqual(len(linked_list), 0)
        self.assertIsNone(linked_list.head)
        self.assertIsNone(linked_list.tail)

    def test_invalid_indexes_raise_without_changing_list(self) -> None:
        linked_list: DoublyLinkedList[int] = DoublyLinkedList()
        linked_list.append(1)

        for operation in (
            lambda: linked_list.insert(-1, 0),
            lambda: linked_list.insert(2, 0),
            lambda: linked_list.remove(-1),
            lambda: linked_list.remove(1),
            lambda: linked_list.get_node(1),
        ):
            with self.subTest(operation=operation), self.assertRaises(IndexError):
                operation()

        self.assertEqual(list(linked_list), [1])


if __name__ == "__main__":
    unittest.main()
