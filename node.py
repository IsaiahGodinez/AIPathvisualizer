"""Node class representing a single cell for algorithm bookkeeping."""

import math


class Node:
    """Algorithm bookkeeping for a grid cell: costs, parent pointer, and heap ordering."""

    def __init__(self, position: tuple[int, int], g_cost: float = math.inf,
                 h_cost: float = 0, parent: "Node | None" = None):
        """Create a node; g_cost defaults to infinity for unvisited nodes."""
        self.position = position
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.parent = parent

    @property
    def f_cost(self) -> float:
        """Total estimated cost: g_cost + h_cost."""
        return self.g_cost + self.h_cost

    def __lt__(self, other: "Node") -> bool:
        """Compare by f_cost; break ties by h_cost."""
        if self.f_cost == other.f_cost:
            return self.h_cost < other.h_cost
        return self.f_cost < other.f_cost

    def __eq__(self, other: object) -> bool:
        """Two nodes are equal if they share the same position."""
        if not isinstance(other, Node):
            return NotImplemented
        return self.position == other.position

    def __hash__(self) -> int:
        """Hash nodes by position."""
        return hash(self.position)

    def __repr__(self) -> str:
        """Debug repr with position and costs."""
        return (f"Node(pos={self.position}, g={self.g_cost}, "
                f"h={self.h_cost}, f={self.f_cost})")
