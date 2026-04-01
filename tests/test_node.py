"""Tests for the Node class."""

import math
import unittest
from node import Node


class TestNode(unittest.TestCase):
    """Test cases for Node."""

    def test_default_values(self):
        """Node initializes with correct defaults."""
        node = Node((0, 0))
        self.assertEqual(node.position, (0, 0))
        self.assertEqual(node.g_cost, math.inf)
        self.assertEqual(node.h_cost, 0)
        self.assertIsNone(node.parent)

    def test_f_cost_property(self):
        """f_cost is computed as g_cost + h_cost."""
        node = Node((1, 2), g_cost=3, h_cost=5)
        self.assertEqual(node.f_cost, 8)

    def test_f_cost_updates_dynamically(self):
        """f_cost reflects changes to g_cost and h_cost."""
        node = Node((0, 0), g_cost=2, h_cost=3)
        self.assertEqual(node.f_cost, 5)
        node.g_cost = 10
        self.assertEqual(node.f_cost, 13)
        node.h_cost = 1
        self.assertEqual(node.f_cost, 11)

    def test_lt_by_f_cost(self):
        """Nodes compare by f_cost first."""
        a = Node((0, 0), g_cost=1, h_cost=2)  # f=3
        b = Node((1, 1), g_cost=2, h_cost=3)  # f=5
        self.assertTrue(a < b)
        self.assertFalse(b < a)

    def test_lt_tiebreak_by_h_cost(self):
        """When f_cost is equal, lower h_cost wins."""
        a = Node((0, 0), g_cost=3, h_cost=2)  # f=5, h=2
        b = Node((1, 1), g_cost=2, h_cost=3)  # f=5, h=3
        self.assertTrue(a < b)
        self.assertFalse(b < a)

    def test_eq_same_position(self):
        """Nodes with the same position are equal regardless of costs."""
        a = Node((2, 3), g_cost=1, h_cost=5)
        b = Node((2, 3), g_cost=99, h_cost=0)
        self.assertEqual(a, b)

    def test_eq_different_position(self):
        """Nodes with different positions are not equal."""
        a = Node((0, 0))
        b = Node((0, 1))
        self.assertNotEqual(a, b)

    def test_hash_consistency(self):
        """Equal nodes produce the same hash."""
        a = Node((5, 5), g_cost=1)
        b = Node((5, 5), g_cost=99)
        self.assertEqual(hash(a), hash(b))

    def test_hash_in_set(self):
        """Nodes can be used in sets, deduplicating by position."""
        s = {Node((0, 0)), Node((0, 0)), Node((1, 1))}
        self.assertEqual(len(s), 2)

    def test_hash_in_dict(self):
        """Nodes can be used as dictionary keys."""
        d = {Node((0, 0)): "start", Node((1, 1)): "goal"}
        self.assertEqual(d[Node((0, 0))], "start")

    def test_parent_chain(self):
        """Parent pointers form a traceable chain."""
        a = Node((0, 0), g_cost=0)
        b = Node((0, 1), g_cost=1, parent=a)
        c = Node((0, 2), g_cost=2, parent=b)
        self.assertIs(c.parent, b)
        self.assertIs(c.parent.parent, a)
        self.assertIsNone(a.parent)

    def test_eq_with_non_node(self):
        """Comparing Node to a non-Node returns NotImplemented."""
        node = Node((0, 0))
        self.assertNotEqual(node, (0, 0))
        self.assertNotEqual(node, "not a node")


if __name__ == "__main__":
    unittest.main()
