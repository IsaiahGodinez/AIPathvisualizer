"""Tests for the Agent class."""

import unittest
from agent import Agent
from constants import (
    ALGORITHM_A_STAR,
    ALGORITHM_GREEDY_BFS,
    ALGORITHM_UCS,
    ALGORITHM_BFS,
    ALGORITHM_DFS,
)


def make_open_grid(height, width):
    """Create a fully open grid."""
    return [[0] * width for _ in range(height)]


def make_known_grid():
    """Create a known 5x5 grid with a specific wall layout.

    Grid layout (S=start, E=end, 1=wall):
        S 0 0 0 0
        0 1 1 0 0
        0 0 0 0 0
        0 0 1 1 0
        0 0 0 0 E

    Shortest path length: 8 steps (path has 9 nodes).
    """
    return [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0],
    ]


def make_unsolvable_grid():
    """Create a grid where no path exists from (0,0) to (4,4)."""
    return [
        [0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]


class TestAgentAStar(unittest.TestCase):
    """Test A* algorithm."""

    def test_finds_path_on_open_grid(self):
        """A* finds a path on a fully open grid."""
        grid = make_open_grid(5, 5)
        agent = Agent(grid, (0, 0), (4, 4))
        path = agent.a_star()
        self.assertTrue(len(path) > 0)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (4, 4))

    def test_optimal_path_open_grid(self):
        """A* finds the optimal (shortest) path on an open grid."""
        grid = make_open_grid(5, 5)
        agent = Agent(grid, (0, 0), (4, 4))
        path = agent.a_star()
        # Manhattan distance = 8, so optimal path has 9 nodes
        self.assertEqual(len(path), 9)

    def test_optimal_path_known_grid(self):
        """A* returns the shortest path on a known grid."""
        grid = make_known_grid()
        agent = Agent(grid, (0, 0), (4, 4))
        path = agent.a_star()
        self.assertEqual(len(path), 9)

    def test_no_path_unsolvable(self):
        """A* returns empty path on unsolvable grid."""
        grid = make_unsolvable_grid()
        agent = Agent(grid, (0, 0), (4, 4))
        path = agent.a_star()
        self.assertEqual(path, [])
        self.assertTrue(agent.is_complete)

    def test_start_equals_end(self):
        """A* handles start == end (path length 1)."""
        grid = make_open_grid(3, 3)
        agent = Agent(grid, (1, 1), (1, 1))
        path = agent.a_star()
        self.assertEqual(path, [(1, 1)])

    def test_metrics_populated(self):
        """Metrics are correctly populated after A*."""
        grid = make_known_grid()
        agent = Agent(grid, (0, 0), (4, 4))
        agent.a_star()
        metrics = agent.get_metrics()
        self.assertEqual(metrics["nodes_explored"], len(agent.explored_order))
        self.assertEqual(metrics["path_cost"], len(agent.path) - 1)
        self.assertGreater(metrics["time_elapsed"], 0)

    def test_explored_order(self):
        """explored_order records nodes in expansion order."""
        grid = make_open_grid(3, 3)
        agent = Agent(grid, (0, 0), (2, 2))
        agent.a_star()
        self.assertEqual(agent.explored_order[0], (0, 0))
        self.assertEqual(agent.explored_order[-1], (2, 2))
        # No duplicates
        self.assertEqual(len(agent.explored_order), len(set(agent.explored_order)))


class TestAgentUCS(unittest.TestCase):
    """Test Uniform Cost Search."""

    def test_finds_optimal_path(self):
        """UCS finds the optimal path (matches A* on uniform grids)."""
        grid = make_known_grid()
        agent = Agent(grid, (0, 0), (4, 4))

        a_star_path = agent.a_star()
        ucs_path = agent.ucs()

        self.assertEqual(len(a_star_path), len(ucs_path))

    def test_finds_path_open_grid(self):
        """UCS finds a valid path on open grid."""
        grid = make_open_grid(5, 5)
        agent = Agent(grid, (0, 0), (4, 4))
        path = agent.ucs()
        self.assertEqual(len(path), 9)

    def test_no_path_unsolvable(self):
        """UCS returns empty path on unsolvable grid."""
        grid = make_unsolvable_grid()
        agent = Agent(grid, (0, 0), (4, 4))
        path = agent.ucs()
        self.assertEqual(path, [])


class TestAgentGreedyBFS(unittest.TestCase):
    """Test Greedy Best-First Search."""

    def test_finds_path(self):
        """Greedy BFS finds a path (not guaranteed optimal)."""
        grid = make_known_grid()
        agent = Agent(grid, (0, 0), (4, 4))
        path = agent.greedy_best_first()
        self.assertTrue(len(path) > 0)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (4, 4))

    def test_no_path_unsolvable(self):
        """Greedy BFS returns empty path on unsolvable grid."""
        grid = make_unsolvable_grid()
        agent = Agent(grid, (0, 0), (4, 4))
        path = agent.greedy_best_first()
        self.assertEqual(path, [])


class TestAgentBFS(unittest.TestCase):
    """Test Breadth-First Search."""

    def test_finds_shortest_path(self):
        """BFS finds the shortest path (same length as A* and UCS)."""
        grid = make_known_grid()
        agent = Agent(grid, (0, 0), (4, 4))

        a_star_path = agent.a_star()
        bfs_path = agent.bfs()

        self.assertEqual(len(bfs_path), len(a_star_path))

    def test_finds_path_open_grid(self):
        """BFS finds a valid path on an open grid."""
        grid = make_open_grid(5, 5)
        agent = Agent(grid, (0, 0), (4, 4))
        path = agent.bfs()
        self.assertEqual(len(path), 9)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (4, 4))

    def test_no_path_unsolvable(self):
        """BFS returns empty path on unsolvable grid."""
        grid = make_unsolvable_grid()
        agent = Agent(grid, (0, 0), (4, 4))
        path = agent.bfs()
        self.assertEqual(path, [])
        self.assertTrue(agent.is_complete)

    def test_explored_order_breadth_first(self):
        """Nodes are explored in breadth-first order (distance 1 before 2)."""
        grid = make_open_grid(5, 5)
        agent = Agent(grid, (0, 0), (4, 4))
        agent.bfs()

        # First explored is start at distance 0
        self.assertEqual(agent.explored_order[0], (0, 0))

        # All distance-1 nodes should come before any distance-2 node
        dist1 = {(0, 1), (1, 0)}
        dist2_example = (1, 1)

        dist1_indices = [agent.explored_order.index(p) for p in dist1
                         if p in agent.explored_order]
        if dist2_example in agent.explored_order:
            dist2_idx = agent.explored_order.index(dist2_example)
            for idx in dist1_indices:
                self.assertLess(idx, dist2_idx)

    def test_metrics_populated(self):
        """Metrics are correctly populated after BFS."""
        grid = make_known_grid()
        agent = Agent(grid, (0, 0), (4, 4))
        agent.bfs()
        metrics = agent.get_metrics()
        self.assertEqual(metrics["nodes_explored"], len(agent.explored_order))
        self.assertEqual(metrics["path_cost"], len(agent.path) - 1)
        self.assertGreater(metrics["time_elapsed"], 0)

    def test_step_matches_full_run(self):
        """Calling step() N times produces the same result as full bfs()."""
        grid = make_known_grid()

        agent_full = Agent(grid, (0, 0), (4, 4))
        full_path = agent_full.bfs()

        agent_step = Agent(grid, (0, 0), (4, 4))
        agent_step.start_algorithm(ALGORITHM_BFS)
        while not agent_step.is_complete:
            agent_step.step()

        self.assertEqual(agent_step.path, full_path)


class TestAgentDFS(unittest.TestCase):
    """Test Depth-First Search."""

    def test_finds_path(self):
        """DFS finds a valid path (not guaranteed shortest)."""
        grid = make_known_grid()
        agent = Agent(grid, (0, 0), (4, 4))
        path = agent.dfs()
        self.assertTrue(len(path) > 0)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (4, 4))

    def test_finds_path_open_grid(self):
        """DFS finds a path on an open grid."""
        grid = make_open_grid(5, 5)
        agent = Agent(grid, (0, 0), (4, 4))
        path = agent.dfs()
        self.assertTrue(len(path) > 0)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (4, 4))

    def test_no_path_unsolvable(self):
        """DFS returns empty path on unsolvable grid."""
        grid = make_unsolvable_grid()
        agent = Agent(grid, (0, 0), (4, 4))
        path = agent.dfs()
        self.assertEqual(path, [])
        self.assertTrue(agent.is_complete)

    def test_metrics_populated(self):
        """Metrics are correctly populated after DFS."""
        grid = make_known_grid()
        agent = Agent(grid, (0, 0), (4, 4))
        agent.dfs()
        metrics = agent.get_metrics()
        self.assertEqual(metrics["nodes_explored"], len(agent.explored_order))
        self.assertEqual(metrics["path_cost"], len(agent.path) - 1)
        self.assertGreater(metrics["time_elapsed"], 0)

    def test_step_matches_full_run(self):
        """Calling step() N times produces the same result as full dfs()."""
        grid = make_known_grid()

        agent_full = Agent(grid, (0, 0), (4, 4))
        full_path = agent_full.dfs()

        agent_step = Agent(grid, (0, 0), (4, 4))
        agent_step.start_algorithm(ALGORITHM_DFS)
        while not agent_step.is_complete:
            agent_step.step()

        self.assertEqual(agent_step.path, full_path)

    def test_no_explored_duplicates(self):
        """explored_order has no duplicate entries."""
        grid = make_open_grid(5, 5)
        agent = Agent(grid, (0, 0), (4, 4))
        agent.dfs()
        self.assertEqual(len(agent.explored_order),
                         len(set(agent.explored_order)))


class TestAgentStepMode(unittest.TestCase):
    """Test step-by-step execution."""

    def test_step_advances_one_iteration(self):
        """Each step() call advances exactly one iteration."""
        grid = make_open_grid(5, 5)
        agent = Agent(grid, (0, 0), (4, 4))
        agent.start_algorithm(ALGORITHM_A_STAR)

        result = agent.step()
        self.assertFalse(result["is_complete"])
        self.assertEqual(result["current_node"], (0, 0))

    def test_step_matches_full_run(self):
        """Calling step() N times produces the same result as full run."""
        grid = make_known_grid()

        # Full run
        agent_full = Agent(grid, (0, 0), (4, 4))
        full_path = agent_full.a_star()

        # Step mode
        agent_step = Agent(grid, (0, 0), (4, 4))
        agent_step.start_algorithm(ALGORITHM_A_STAR)
        while not agent_step.is_complete:
            agent_step.step()

        self.assertEqual(agent_step.path, full_path)

    def test_step_is_complete_when_done(self):
        """step() sets is_complete when goal is found."""
        grid = make_open_grid(3, 3)
        agent = Agent(grid, (0, 0), (2, 2))
        agent.start_algorithm(ALGORITHM_A_STAR)

        while not agent.is_complete:
            result = agent.step()

        self.assertTrue(result["is_complete"])
        self.assertTrue(agent.is_complete)
        self.assertTrue(len(agent.path) > 0)

    def test_step_no_path(self):
        """step() completes with empty path on unsolvable grid."""
        grid = make_unsolvable_grid()
        agent = Agent(grid, (0, 0), (4, 4))
        agent.start_algorithm(ALGORITHM_A_STAR)

        while not agent.is_complete:
            agent.step()

        self.assertTrue(agent.is_complete)
        self.assertEqual(agent.path, [])


class TestAgentEdgeCases(unittest.TestCase):
    """Edge case tests."""

    def test_tiny_grid_2x2(self):
        """2x2 grid works correctly."""
        grid = [[0, 0], [0, 0]]
        agent = Agent(grid, (0, 0), (1, 1))
        path = agent.a_star()
        self.assertEqual(len(path), 3)  # (0,0)->(0,1)->(1,1) or (0,0)->(1,0)->(1,1)

    def test_tiny_grid_3x3(self):
        """3x3 grid works correctly."""
        grid = make_open_grid(3, 3)
        agent = Agent(grid, (0, 0), (2, 2))
        path = agent.a_star()
        self.assertEqual(len(path), 5)

    def test_manhattan_distance(self):
        """Manhattan distance computes correctly."""
        self.assertEqual(Agent.manhattan_distance((0, 0), (3, 4)), 7)
        self.assertEqual(Agent.manhattan_distance((2, 5), (2, 5)), 0)
        self.assertEqual(Agent.manhattan_distance((0, 0), (0, 0)), 0)

    def test_reset_clears_state(self):
        """Reset clears all algorithm state."""
        grid = make_open_grid(5, 5)
        agent = Agent(grid, (0, 0), (4, 4))
        agent.a_star()
        self.assertTrue(len(agent.path) > 0)

        agent.reset()
        self.assertEqual(agent.path, [])
        self.assertEqual(agent.explored_order, [])
        self.assertEqual(len(agent.open_set), 0)
        self.assertEqual(len(agent.closed_set), 0)
        self.assertFalse(agent.is_complete)
        self.assertFalse(agent.is_running)

    def test_path_cost_matches_path_length(self):
        """path_cost equals len(path) - 1."""
        grid = make_open_grid(5, 5)
        agent = Agent(grid, (0, 0), (4, 4))
        agent.a_star()
        self.assertEqual(agent.metrics["path_cost"], len(agent.path) - 1)

    def test_all_algorithms_on_same_grid(self):
        """All five algorithms find valid paths on the same grid."""
        grid = make_known_grid()
        agent = Agent(grid, (0, 0), (4, 4))

        a_star_path = agent.a_star()
        ucs_path = agent.ucs()
        greedy_path = agent.greedy_best_first()
        bfs_path = agent.bfs()
        dfs_path = agent.dfs()

        # All find a path
        self.assertTrue(len(a_star_path) > 0)
        self.assertTrue(len(ucs_path) > 0)
        self.assertTrue(len(greedy_path) > 0)
        self.assertTrue(len(bfs_path) > 0)
        self.assertTrue(len(dfs_path) > 0)

        # A*, UCS, and BFS are optimal (same length on uniform cost grid)
        self.assertEqual(len(a_star_path), len(ucs_path))
        self.assertEqual(len(a_star_path), len(bfs_path))

        # Greedy and DFS find paths but may be longer
        self.assertGreaterEqual(len(greedy_path), len(a_star_path))
        self.assertGreaterEqual(len(dfs_path), len(a_star_path))


if __name__ == "__main__":
    unittest.main()
