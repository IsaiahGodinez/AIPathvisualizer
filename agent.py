"""Agent class containing A*, Greedy BFS, UCS, BFS, and DFS search algorithms."""

import heapq
import time
from collections import deque

from node import Node
from constants import (
    DIRECTIONS,
    ALGORITHM_A_STAR,
    ALGORITHM_GREEDY_BFS,
    ALGORITHM_UCS,
    ALGORITHM_BFS,
    ALGORITHM_DFS,
)


class Agent:
    """Implements A*, Greedy BFS, UCS, BFS, and DFS for full-run and step-by-step use."""

    def __init__(self, grid: list[list[int]], start: tuple[int, int],
                 end: tuple[int, int]):
        """Set up agent state for the given grid, start, and end."""
        self.grid = grid
        self.start = start
        self.end = end
        self.grid_height = len(grid)
        self.grid_width = len(grid[0]) if grid else 0

        # Algorithm state
        self.open_set: list = []
        self.closed_set: set[tuple[int, int]] = set()
        self.path: list[tuple[int, int]] = []
        self.explored_order: list[tuple[int, int]] = []
        self.frontier_snapshots: list = []
        self.is_complete: bool = False
        self.is_running: bool = False
        self.metrics: dict = {
            "nodes_explored": 0,
            "path_cost": 0,
            "time_elapsed": 0.0,
        }

        # Internal state for step mode
        self._algorithm: str = ""
        self._node_map: dict[tuple[int, int], Node] = {}
        self._start_time: float = 0.0
        self._counter: int = 0  # Tiebreaker for heap stability
        self._queue: deque[Node] | list[Node] = []  # For BFS (deque) / DFS (list)
        self._in_queue: set[tuple[int, int]] = set()  # BFS duplicate prevention

    def a_star(self) -> list[tuple[int, int]]:
        """Run A* using f(n) = g(n) + h(n); return the path or []."""
        self.reset()
        self._algorithm = ALGORITHM_A_STAR
        self._start_time = time.time()
        self._init_open_set()

        while self.open_set and not self.is_complete:
            self._step_internal()

        self.is_complete = True
        self.metrics["time_elapsed"] = time.time() - self._start_time
        self.is_running = False
        return self.path

    def greedy_best_first(self) -> list[tuple[int, int]]:
        """Run Greedy BFS (priority = h only, not optimal); return the path or []."""
        self.reset()
        self._algorithm = ALGORITHM_GREEDY_BFS
        self._start_time = time.time()
        self._init_open_set()

        while self.open_set and not self.is_complete:
            self._step_internal()

        self.is_complete = True
        self.metrics["time_elapsed"] = time.time() - self._start_time
        self.is_running = False
        return self.path

    def ucs(self) -> list[tuple[int, int]]:
        """Run UCS (priority = g only, no heuristic); return the path or []."""
        self.reset()
        self._algorithm = ALGORITHM_UCS
        self._start_time = time.time()
        self._init_open_set()

        while self.open_set and not self.is_complete:
            self._step_internal()

        self.is_complete = True
        self.metrics["time_elapsed"] = time.time() - self._start_time
        self.is_running = False
        return self.path

    def bfs(self) -> list[tuple[int, int]]:
        """Run BFS (FIFO, shortest path on unweighted grid); return the path or []."""
        self.reset()
        self._algorithm = ALGORITHM_BFS
        self._start_time = time.time()
        self._init_bfs_dfs_queue()

        while self._queue and not self.is_complete:
            self._step_bfs_internal()

        self.is_complete = True
        self.metrics["time_elapsed"] = time.time() - self._start_time
        self.is_running = False
        return self.path

    def dfs(self) -> list[tuple[int, int]]:
        """Run DFS (LIFO, path not guaranteed shortest); return the path or []."""
        self.reset()
        self._algorithm = ALGORITHM_DFS
        self._start_time = time.time()
        self._init_bfs_dfs_queue()

        while self._queue and not self.is_complete:
            self._step_dfs_internal()

        self.is_complete = True
        self.metrics["time_elapsed"] = time.time() - self._start_time
        self.is_running = False
        return self.path

    def start_algorithm(self, algorithm: str) -> None:
        """Prepare the selected algorithm for step-by-step execution."""
        self.reset()
        self._algorithm = algorithm
        self._start_time = time.time()
        if algorithm in (ALGORITHM_BFS, ALGORITHM_DFS):
            self._init_bfs_dfs_queue()
        else:
            self._init_open_set()
        self.is_running = True

    def step(self) -> dict:
        """Run one step of the selected algorithm.

        Dispatches to the correct internal step function.
        Returns a dict with current_node, new_frontier_nodes, and is_complete.
        """
        if self._algorithm in (ALGORITHM_BFS, ALGORITHM_DFS):
            container_empty = not self._queue
        else:
            container_empty = not self.open_set

        if self.is_complete or container_empty:
            if not self.is_complete:
                self.is_complete = True
                self.is_running = False
                self.metrics["time_elapsed"] = time.time() - self._start_time
            return {
                "current_node": None,
                "new_frontier_nodes": [],
                "is_complete": True,
            }

        if self._algorithm == ALGORITHM_BFS:
            result = self._step_bfs_internal()
        elif self._algorithm == ALGORITHM_DFS:
            result = self._step_dfs_internal()
        else:
            result = self._step_internal()

        if self.is_complete:
            self.metrics["time_elapsed"] = time.time() - self._start_time
            self.is_running = False
        return result

    def _init_open_set(self) -> None:
        """Seed the frontier with the start node."""
        start_node = Node(self.start, g_cost=0,
                          h_cost=self.manhattan_distance(self.start, self.end))
        self._node_map[self.start] = start_node
        priority = self._get_priority(start_node)
        heapq.heappush(self.open_set, (priority, self._counter, start_node))
        self._counter += 1
        self.is_running = True

    def _get_priority(self, node: Node) -> float:
        """Return the heap priority for a node based on the current algorithm."""
        if self._algorithm == ALGORITHM_A_STAR:
            return node.f_cost
        elif self._algorithm == ALGORITHM_GREEDY_BFS:
            return node.h_cost
        elif self._algorithm == ALGORITHM_UCS:
            return node.g_cost
        return node.f_cost

    def _step_internal(self) -> dict:
        """Run one iteration of the heap-based search (A*, Greedy BFS, UCS).

        Pops the best node, skips if already explored (lazy deletion),
        expands neighbors, and snapshots the frontier.
        Returns a dict with current_node, new_frontier_nodes, is_complete.
        """
        if not self.open_set:
            self.is_complete = True
            return {
                "current_node": None,
                "new_frontier_nodes": [],
                "is_complete": True,
            }

        _priority, _count, current = heapq.heappop(self.open_set)

        if current.position in self.closed_set:  # lazy deletion
            return {
                "current_node": current.position,
                "new_frontier_nodes": [],
                "is_complete": False,
            }

        self.closed_set.add(current.position)
        self.explored_order.append(current.position)
        self.metrics["nodes_explored"] = len(self.explored_order)

        if current.position == self.end:
            self.path = self.reconstruct_path(current)
            self.metrics["path_cost"] = len(self.path) - 1 if self.path else 0
            self.is_complete = True
            return {
                "current_node": current.position,
                "new_frontier_nodes": [],
                "is_complete": True,
            }

        new_frontier = []
        for neighbor_pos in self.get_neighbors(current.position):
            if neighbor_pos in self.closed_set:
                continue

            tentative_g = current.g_cost + 1

            neighbor_node = self._node_map.get(neighbor_pos)
            if neighbor_node is None or tentative_g < neighbor_node.g_cost:
                if neighbor_node is None:
                    neighbor_node = Node(neighbor_pos)
                    self._node_map[neighbor_pos] = neighbor_node

                neighbor_node.g_cost = tentative_g
                neighbor_node.h_cost = self.manhattan_distance(
                    neighbor_pos, self.end
                )
                neighbor_node.parent = current

                priority = self._get_priority(neighbor_node)
                heapq.heappush(
                    self.open_set,
                    (priority, self._counter, neighbor_node)
                )
                self._counter += 1
                new_frontier.append(neighbor_pos)

        self.frontier_snapshots.append(
            [item[2].position for item in self.open_set]
        )

        return {
            "current_node": current.position,
            "new_frontier_nodes": new_frontier,
            "is_complete": False,
        }

    def _init_bfs_dfs_queue(self) -> None:
        """Initialize the queue/stack with the start node for BFS or DFS."""
        start_node = Node(self.start, g_cost=0)
        self._node_map[self.start] = start_node
        if self._algorithm == ALGORITHM_BFS:
            self._queue = deque([start_node])
            self._in_queue = {self.start}
        else:  # DFS
            self._queue = [start_node]
            self._in_queue = set()
        self.is_running = True

    def _step_bfs_internal(self) -> dict:
        """Run one BFS iteration (FIFO dequeue).

        Returns a dict with current_node, new_frontier_nodes, is_complete.
        """
        if not self._queue:
            self.is_complete = True
            return {
                "current_node": None,
                "new_frontier_nodes": [],
                "is_complete": True,
            }

        current = self._queue.popleft()
        self._in_queue.discard(current.position)

        self.closed_set.add(current.position)
        self.explored_order.append(current.position)
        self.metrics["nodes_explored"] = len(self.explored_order)

        if current.position == self.end:
            self.path = self.reconstruct_path(current)
            self.metrics["path_cost"] = len(self.path) - 1 if self.path else 0
            self.is_complete = True
            return {
                "current_node": current.position,
                "new_frontier_nodes": [],
                "is_complete": True,
            }

        new_frontier: list[tuple[int, int]] = []
        for neighbor_pos in self.get_neighbors(current.position):
            if neighbor_pos in self.closed_set:
                continue
            if neighbor_pos in self._in_queue:
                continue

            neighbor_node = Node(neighbor_pos,
                                 g_cost=current.g_cost + 1)
            neighbor_node.parent = current
            self._node_map[neighbor_pos] = neighbor_node
            self._queue.append(neighbor_node)
            self._in_queue.add(neighbor_pos)
            new_frontier.append(neighbor_pos)

        # Mirror queue into open_set for visualization
        self.open_set = list(self._queue)

        return {
            "current_node": current.position,
            "new_frontier_nodes": new_frontier,
            "is_complete": False,
        }

    def _step_dfs_internal(self) -> dict:
        """Run one DFS iteration (LIFO pop).

        Returns a dict with current_node, new_frontier_nodes, is_complete.
        """
        if not self._queue:
            self.is_complete = True
            return {
                "current_node": None,
                "new_frontier_nodes": [],
                "is_complete": True,
            }

        current = self._queue.pop()

        if current.position in self.closed_set:  # DFS can push duplicates
            return {
                "current_node": current.position,
                "new_frontier_nodes": [],
                "is_complete": False,
            }

        self.closed_set.add(current.position)
        self.explored_order.append(current.position)
        self.metrics["nodes_explored"] = len(self.explored_order)

        if current.position == self.end:
            self.path = self.reconstruct_path(current)
            self.metrics["path_cost"] = len(self.path) - 1 if self.path else 0
            self.is_complete = True
            return {
                "current_node": current.position,
                "new_frontier_nodes": [],
                "is_complete": True,
            }

        new_frontier: list[tuple[int, int]] = []
        for neighbor_pos in self.get_neighbors(current.position):
            if neighbor_pos in self.closed_set:
                continue

            neighbor_node = Node(neighbor_pos,
                                 g_cost=current.g_cost + 1)
            neighbor_node.parent = current
            self._node_map[neighbor_pos] = neighbor_node
            self._queue.append(neighbor_node)
            new_frontier.append(neighbor_pos)

        # Mirror stack into open_set for visualization
        self.open_set = list(self._queue)

        return {
            "current_node": current.position,
            "new_frontier_nodes": new_frontier,
            "is_complete": False,
        }

    def get_neighbors(self, position: tuple[int, int]) -> list[tuple[int, int]]:
        """Return in-bounds, open neighbors (4-directional)."""
        neighbors = []
        row, col = position
        for dr, dc in DIRECTIONS:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.grid_height and 0 <= nc < self.grid_width:
                if self.grid[nr][nc] == 0:
                    neighbors.append((nr, nc))
        return neighbors

    def reconstruct_path(self, node: Node) -> list[tuple[int, int]]:
        """Trace parent pointers from goal back to start; return ordered path."""
        path = []
        current = node
        while current is not None:
            path.append(current.position)
            current = current.parent
        path.reverse()
        return path

    @staticmethod
    def manhattan_distance(a: tuple[int, int], b: tuple[int, int]) -> int:
        """Return Manhattan distance between two (row, col) positions."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def reset(self) -> None:
        """Clear all state for a fresh run."""
        self.open_set = []
        self.closed_set = set()
        self.path = []
        self.explored_order = []
        self.frontier_snapshots = []
        self.is_complete = False
        self.is_running = False
        self.metrics = {
            "nodes_explored": 0,
            "path_cost": 0,
            "time_elapsed": 0.0,
        }
        self._node_map = {}
        self._counter = 0
        self._queue = []
        self._in_queue = set()

    def get_metrics(self) -> dict:
        """Return a copy of the current performance metrics."""
        return self.metrics.copy()
