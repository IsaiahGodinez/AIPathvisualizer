"""Node class representing a single cell for algorithm bookkeeping."""

import math


class Node:
    """Represents a single cell on the grid for pathfinding algorithms.

    Node does not store wall/start/goal state — that lives in the grid.
    This class is purely for algorithm bookkeeping: tracking costs, parent
    pointers, and supporting priority queue ordering.
    """

    def __init__(self, position: tuple[int, int], g_cost: float = math.inf,
                 h_cost: float = 0, parent: "Node | None" = None):
        """Initialize a Node.

        Args:
            position: (row, col) coordinates on the grid.
            g_cost: Cost from start to this node. Defaults to infinity.
            h_cost: Heuristic estimate from this node to goal. Defaults to 0.
            parent: Reference to the previous node in the path.
        """
        self.position = position
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.parent = parent

    @property
    def f_cost(self) -> float:
        """Total estimated cost: g_cost + h_cost."""
        return self.g_cost + self.h_cost

    def __lt__(self, other: "Node") -> bool:
        """Compare nodes by f_cost for priority queue ordering.

        Breaks ties by h_cost (lower h_cost preferred).
        """
        if self.f_cost == other.f_cost:
            return self.h_cost < other.h_cost
        return self.f_cost < other.f_cost

    def __eq__(self, other: object) -> bool:
        """Two nodes are equal if they share the same position."""
        if not isinstance(other, Node):
            return NotImplemented
        return self.position == other.position

    def __hash__(self) -> int:
        """Hash by position so nodes can be used in sets and dicts."""
        return hash(self.position)

    def __repr__(self) -> str:
        """Return a string representation of the node."""
        return (f"Node(pos={self.position}, g={self.g_cost}, "
                f"h={self.h_cost}, f={self.f_cost})")
