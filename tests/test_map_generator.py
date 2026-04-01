"""Tests for the MapGenerator class (DFS maze generation)."""

import unittest
from collections import deque

from map_generator import MapGenerator
from constants import MIN_DISTINCT_PATHS


class TestMapGeneratorGrid(unittest.TestCase):
    """Grid structure and dimension tests."""

    def test_grid_dimensions_odd(self):
        """Odd dimensions are kept as-is."""
        mg = MapGenerator(grid_width=11, grid_height=9)
        self.assertEqual(len(mg.grid), 9)
        self.assertEqual(len(mg.grid[0]), 11)

    def test_even_dimensions_rounded_up(self):
        """Even dimensions are rounded up to the nearest odd number."""
        mg = MapGenerator(grid_width=10, grid_height=8)
        self.assertEqual(mg.grid_width % 2, 1)
        self.assertEqual(mg.grid_height % 2, 1)
        self.assertEqual(len(mg.grid), mg.grid_height)
        self.assertEqual(len(mg.grid[0]), mg.grid_width)

    def test_start_not_wall(self):
        """Start cell is never a wall."""
        mg = MapGenerator(grid_width=15, grid_height=15)
        self.assertEqual(mg.grid[mg.start[0]][mg.start[1]], 0)

    def test_end_not_wall(self):
        """End cell is never a wall."""
        mg = MapGenerator(grid_width=15, grid_height=15)
        self.assertEqual(mg.grid[mg.end[0]][mg.end[1]], 0)

    def test_start_end_far_apart(self):
        """Start and end are placed at opposite corners."""
        mg = MapGenerator(grid_width=25, grid_height=25)
        self.assertEqual(mg.start, (0, 0))
        # End should be near the bottom-right on an even-indexed cell
        self.assertGreater(mg.end[0], mg.grid_height // 2)
        self.assertGreater(mg.end[1], mg.grid_width // 2)

    def test_start_end_on_even_indices(self):
        """Start and end land on even-indexed cells (valid passage cells)."""
        mg = MapGenerator(grid_width=25, grid_height=25)
        self.assertEqual(mg.start[0] % 2, 0)
        self.assertEqual(mg.start[1] % 2, 0)
        self.assertEqual(mg.end[0] % 2, 0)
        self.assertEqual(mg.end[1] % 2, 0)


class TestMapGeneratorPaths(unittest.TestCase):
    """Path validation tests."""

    def test_at_least_three_paths(self):
        """Grid has at least 3 distinct paths from start to end."""
        mg = MapGenerator(grid_width=15, grid_height=15)
        self.assertTrue(mg.validate_paths())

    def test_three_distinct_paths_on_many_grids(self):
        """At least 3 distinct paths on 12 random grids."""
        for _ in range(12):
            mg = MapGenerator(grid_width=21, grid_height=21)
            count = mg._count_distinct_paths(max_count=3)
            self.assertGreaterEqual(
                count, MIN_DISTINCT_PATHS,
                f"Only {count} distinct paths found (need {MIN_DISTINCT_PATHS})"
            )

    def test_no_isolated_cells(self):
        """Every open cell is reachable from start via BFS on 12 random grids."""
        for _ in range(12):
            mg = MapGenerator(grid_width=15, grid_height=15)

            visited: set[tuple[int, int]] = set()
            queue = deque([mg.start])
            visited.add(mg.start)
            while queue:
                current = queue.popleft()
                for neighbor in mg.get_neighbors(current):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            for row in range(mg.grid_height):
                for col in range(mg.grid_width):
                    if mg.grid[row][col] == 0:
                        self.assertIn(
                            (row, col), visited,
                            f"Open cell ({row}, {col}) is unreachable"
                        )


class TestMapGeneratorCarve(unittest.TestCase):
    """Tests for the DFS maze carving phase."""

    def test_perfect_maze_fully_connected(self):
        """After carving (before extra wall removal) every open cell is reachable."""
        mg = MapGenerator.__new__(MapGenerator)
        mg.grid_width = 15
        mg.grid_height = 15
        mg.grid = [[1] * mg.grid_width for _ in range(mg.grid_height)]
        mg.start = (0, 0)
        mg.end = (mg.grid_height - 2 if mg.grid_height % 2 == 0
                  else mg.grid_height - 1,
                  mg.grid_width - 2 if mg.grid_width % 2 == 0
                  else mg.grid_width - 1)
        mg.place_start_end()
        mg._carve_maze()

        # Flood fill
        visited: set[tuple[int, int]] = set()
        queue = deque([mg.start])
        visited.add(mg.start)
        while queue:
            current = queue.popleft()
            for neighbor in mg.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        for row in range(mg.grid_height):
            for col in range(mg.grid_width):
                if mg.grid[row][col] == 0:
                    self.assertIn(
                        (row, col), visited,
                        f"Open cell ({row}, {col}) unreachable in perfect maze"
                    )


class TestMapGeneratorNeighbors(unittest.TestCase):
    """Tests for get_neighbors()."""

    def test_get_neighbors_excludes_walls(self):
        """Neighbors exclude wall cells."""
        mg = MapGenerator(grid_width=5, grid_height=5)
        # Manually wall off a neighbor
        mg.grid[1][2] = 1
        neighbors = mg.get_neighbors((2, 2))
        self.assertNotIn((1, 2), neighbors)

    def test_get_neighbors_respects_bounds(self):
        """Corner cell does not return out-of-bounds neighbors."""
        mg = MapGenerator(grid_width=5, grid_height=5)
        neighbors = mg.get_neighbors((0, 0))
        for r, c in neighbors:
            self.assertGreaterEqual(r, 0)
            self.assertGreaterEqual(c, 0)
            self.assertLess(r, mg.grid_height)
            self.assertLess(c, mg.grid_width)


class TestMapGeneratorToggle(unittest.TestCase):
    """Tests for toggle_wall()."""

    def test_toggle_wall_rejects_start(self):
        """Cannot toggle the start cell."""
        mg = MapGenerator(grid_width=15, grid_height=15)
        self.assertFalse(mg.toggle_wall(mg.start))

    def test_toggle_wall_rejects_end(self):
        """Cannot toggle the end cell."""
        mg = MapGenerator(grid_width=15, grid_height=15)
        self.assertFalse(mg.toggle_wall(mg.end))

    def test_toggle_wall_rejects_if_unsolvable(self):
        """Toggle is rejected if it would drop below MIN_DISTINCT_PATHS."""
        mg = MapGenerator(grid_width=5, grid_height=5)
        mg.grid = [
            [0, 0, 0, 0, 0],
            [1, 1, 0, 1, 1],
            [1, 1, 0, 1, 1],
            [1, 1, 0, 1, 1],
            [0, 0, 0, 0, 0],
        ]
        mg.start = (0, 0)
        mg.end = (4, 4)
        # Only one corridor — blocking (2, 2) should be rejected
        result = mg.toggle_wall((2, 2))
        self.assertFalse(result)


class TestMapGeneratorMisc(unittest.TestCase):
    """Reset and edge cases."""

    def test_reset_regenerates(self):
        """Reset produces a new valid grid."""
        mg = MapGenerator(grid_width=15, grid_height=15)
        mg.reset()
        self.assertTrue(mg.validate_paths())
        self.assertEqual(len(mg.grid), mg.grid_height)
        self.assertEqual(len(mg.grid[0]), mg.grid_width)

    def test_small_grid_5x5(self):
        """5×5 (smallest practical odd grid) generates and is valid."""
        mg = MapGenerator(grid_width=5, grid_height=5)
        self.assertEqual(mg.grid_width, 5)
        self.assertEqual(mg.grid_height, 5)
        path = mg._bfs(mg.start, mg.end)
        self.assertIsNotNone(path)

    def test_solvable_maze(self):
        """Generated maze is always solvable."""
        mg = MapGenerator(grid_width=15, grid_height=15)
        path = mg._bfs(mg.start, mg.end)
        self.assertIsNotNone(path)

    def test_odd_grid_dimensions_enforced(self):
        """Requesting even sizes yields odd actual dimensions."""
        for w, h in [(10, 10), (20, 14), (8, 6)]:
            mg = MapGenerator(grid_width=w, grid_height=h)
            self.assertEqual(mg.grid_width % 2, 1,
                             f"width {mg.grid_width} is not odd for input {w}")
            self.assertEqual(mg.grid_height % 2, 1,
                             f"height {mg.grid_height} is not odd for input {h}")


if __name__ == "__main__":
    unittest.main()
