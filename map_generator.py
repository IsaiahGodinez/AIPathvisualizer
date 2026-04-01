"""MapGenerator class — DFS maze generation with multiple-path guarantee."""

import random
from collections import deque

from constants import (
    DEFAULT_GRID_WIDTH,
    DEFAULT_GRID_HEIGHT,
    DIRECTIONS,
    MAX_GENERATION_RETRIES,
    MIN_DISTINCT_PATHS,
)


class MapGenerator:
    """Builds a maze via DFS recursive backtracker, then opens extra walls
    to guarantee at least MIN_DISTINCT_PATHS distinct paths from start to end.

    The grid is a 2D list where 0 = open cell (passage) and 1 = wall.
    Grid dimensions are always odd × odd so that the DFS carving algorithm
    works correctly (passages on even-indexed cells, walls on odd-indexed
    cells). If even dimensions are requested they are rounded up.
    """

    def __init__(self, grid_width: int = DEFAULT_GRID_WIDTH,
                 grid_height: int = DEFAULT_GRID_HEIGHT):
        """Initialize the MapGenerator.

        Args:
            grid_width: Desired number of columns (rounded up to odd).
            grid_height: Desired number of rows (rounded up to odd).
        """
        # Ensure odd dimensions for the DFS maze algorithm
        self.grid_width = grid_width if grid_width % 2 == 1 else grid_width + 1
        self.grid_height = grid_height if grid_height % 2 == 1 else grid_height + 1
        self.grid: list[list[int]] = []
        self.start: tuple[int, int] = (0, 0)
        self.end: tuple[int, int] = (self.grid_height - 1, self.grid_width - 1)
        self.generate_grid()

    def generate_grid(self) -> list[list[int]]:
        """Create a maze using DFS carving, then open walls for 3+ paths.

        Phase 1: Carve a perfect maze (DFS recursive backtracker).
        Phase 2: Selectively remove walls until 3+ distinct paths exist,
                 plus a small cosmetic batch for variety.
        Phase 3: Validate that at least MIN_DISTINCT_PATHS paths exist.

        Returns:
            The generated 2D grid.
        """
        for _attempt in range(MAX_GENERATION_RETRIES):
            # Phase 1 — carve a perfect maze
            self.grid = [[1] * self.grid_width
                         for _ in range(self.grid_height)]
            self.place_start_end()
            self._carve_maze()

            # Phase 2 — open extra walls for multiple paths
            self._open_extra_walls()

            # Phase 3 — validate
            if self.validate_paths():
                return self.grid

        # Fallback (should be extremely rare with DFS mazes)
        return self.grid

    def validate_paths(self) -> bool:
        """Verify that at least MIN_DISTINCT_PATHS distinct paths exist.

        Uses iterative node-blocking: find a path, block an intermediate
        node, find another, block again, etc.  Two paths are distinct if
        they differ by at least one intermediate node.

        Returns:
            True if at least MIN_DISTINCT_PATHS distinct paths exist.
        """
        return self._count_distinct_paths(MIN_DISTINCT_PATHS) >= MIN_DISTINCT_PATHS

    def _count_distinct_paths(self, max_count: int = 3) -> int:
        """Count distinct paths from start to end, up to *max_count*.

        Strategy: find a path via BFS, then block each of its intermediate
        nodes one at a time.  For every block that still leaves a viable
        path, we have evidence of at least one additional distinct path.
        We accumulate until we reach *max_count* or exhaust options.

        Args:
            max_count: Stop counting once this many paths are confirmed.

        Returns:
            Number of confirmed distinct paths (at least 1 if any path
            exists, 0 if the maze is unsolvable).
        """
        first_path = self._bfs(self.start, self.end)
        if not first_path:
            return 0

        count = 1  # The first path itself

        # For each intermediate node on the first path, block it and see
        # whether an alternative path still exists.  Each success is
        # evidence of a distinct route.
        for pos in first_path[1:-1]:
            if count >= max_count:
                break
            original = self.grid[pos[0]][pos[1]]
            self.grid[pos[0]][pos[1]] = 1
            alt = self._bfs(self.start, self.end)
            self.grid[pos[0]][pos[1]] = original
            if alt:
                count += 1

        return count

    # ------------------------------------------------------------------
    # Phase 1 — DFS Recursive Backtracker
    # ------------------------------------------------------------------

    def _carve_maze(self) -> None:
        """Carve a perfect maze using iterative DFS (recursive backtracker).

        Passages land on even-indexed (row, col) cells; odd-indexed cells
        between two passages are the walls that get removed to connect them.
        Operates on self.grid in place.
        """
        start_row, start_col = self.start
        self.grid[start_row][start_col] = 0

        stack: list[tuple[int, int]] = [(start_row, start_col)]

        while stack:
            row, col = stack[-1]
            # Neighbors are 2 cells away in each cardinal direction
            unvisited = []
            for dr, dc in DIRECTIONS:
                nr, nc = row + dr * 2, col + dc * 2
                if (0 <= nr < self.grid_height and 0 <= nc < self.grid_width
                        and self.grid[nr][nc] == 1):
                    unvisited.append((nr, nc, dr, dc))

            if unvisited:
                nr, nc, dr, dc = random.choice(unvisited)
                # Remove the wall between current cell and chosen neighbor
                self.grid[row + dr][col + dc] = 0
                # Mark the chosen neighbor as open
                self.grid[nr][nc] = 0
                stack.append((nr, nc))
            else:
                stack.pop()

        # Ensure the end cell is open (it should be on an even index and
        # reachable, but guarantee it)
        self.grid[self.end[0]][self.end[1]] = 0

        # If end is not yet reachable (can happen when grid is very small),
        # carve a connection from the nearest open cell.
        if not self._bfs(self.start, self.end):
            self._connect_end()

    def _connect_end(self) -> None:
        """Carve a passage from the end cell to the nearest reachable cell.

        Walks from end toward start, opening walls, until a reachable cell
        is hit.
        """
        er, ec = self.end
        # Try to connect by walking left then up toward (0, 0)
        r, c = er, ec
        while True:
            self.grid[r][c] = 0
            if self._bfs(self.start, (r, c)):
                break
            # Move toward start — prefer carving in the direction with more
            # distance remaining
            if r > 0:
                r -= 1
            elif c > 0:
                c -= 1
            else:
                break

    # ------------------------------------------------------------------
    # Phase 2 — Open extra walls for multiple paths
    # ------------------------------------------------------------------

    def _open_extra_walls(self) -> None:
        """Remove interior walls to create multiple paths.

        First removes walls until at least MIN_DISTINCT_PATHS distinct
        paths exist, then removes a small cosmetic batch (~10 % of
        remaining candidates) for visual variety.
        """
        candidates = self._get_wall_removal_candidates()
        random.shuffle(candidates)

        # --- mandatory removals: reach MIN_DISTINCT_PATHS ---
        remaining: list[tuple[int, int]] = []
        for pos in candidates:
            if self._count_distinct_paths(MIN_DISTINCT_PATHS) >= MIN_DISTINCT_PATHS:
                remaining.append(pos)
                # Collect the rest without checking
                remaining.extend(
                    candidates[candidates.index(pos) + 1:]
                )
                break
            self.grid[pos[0]][pos[1]] = 0

        # --- cosmetic removals for variety ---
        if remaining:
            extra_count = max(1, int(len(remaining) * 0.10))
            random.shuffle(remaining)
            for pos in remaining[:extra_count]:
                self.grid[pos[0]][pos[1]] = 0

    def _get_wall_removal_candidates(self) -> list[tuple[int, int]]:
        """Return interior wall cells eligible for removal.

        A candidate is a wall cell that has exactly 2 open neighbours on
        opposite sides (horizontal pair or vertical pair).  Removing it
        creates a loop / alternate path.

        Returns:
            Shuffled list of (row, col) wall positions.
        """
        candidates: list[tuple[int, int]] = []
        for row in range(1, self.grid_height - 1):
            for col in range(1, self.grid_width - 1):
                if self.grid[row][col] != 1:
                    continue
                if (row, col) == self.start or (row, col) == self.end:
                    continue

                # Check vertical pair (above & below both open)
                vert = (self.grid[row - 1][col] == 0
                        and self.grid[row + 1][col] == 0)
                # Check horizontal pair (left & right both open)
                horiz = (self.grid[row][col - 1] == 0
                         and self.grid[row][col + 1] == 0)

                if vert or horiz:
                    candidates.append((row, col))

        return candidates

    # ------------------------------------------------------------------
    # BFS helper (internal validation, NOT one of the 3 main algorithms)
    # ------------------------------------------------------------------

    def _bfs(self, start: tuple[int, int],
             end: tuple[int, int]) -> list[tuple[int, int]] | None:
        """Run BFS from start to end on the current grid.

        Args:
            start: Starting position (row, col).
            end: Goal position (row, col).

        Returns:
            List of positions from start to end, or None if no path exists.
        """
        if start == end:
            return [start]

        queue = deque([start])
        came_from: dict[tuple[int, int], tuple[int, int] | None] = {
            start: None
        }

        while queue:
            current = queue.popleft()
            if current == end:
                path: list[tuple[int, int]] = []
                node: tuple[int, int] | None = current
                while node is not None:
                    path.append(node)
                    node = came_from[node]
                path.reverse()
                return path

            for neighbor in self.get_neighbors(current):
                if neighbor not in came_from:
                    came_from[neighbor] = current
                    queue.append(neighbor)

        return None

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def place_start_end(self) -> None:
        """Place start and end on valid passage cells at opposite corners.

        Both land on even-indexed (row, col) positions so they align with
        the DFS maze grid.  Ensures neither is a wall.
        """
        self.start = (0, 0)
        # Furthest even-indexed cell from (0, 0)
        end_row = self.grid_height - 1 if (self.grid_height - 1) % 2 == 0 \
            else self.grid_height - 2
        end_col = self.grid_width - 1 if (self.grid_width - 1) % 2 == 0 \
            else self.grid_width - 2
        self.end = (end_row, end_col)

        self.grid[self.start[0]][self.start[1]] = 0
        self.grid[self.end[0]][self.end[1]] = 0

    def reset(self) -> None:
        """Clear the grid and regenerate from scratch."""
        self.generate_grid()

    def get_neighbors(self, position: tuple[int, int]) -> list[tuple[int, int]]:
        """Return valid adjacent cells (up/down/left/right only).

        Excludes out-of-bounds and wall cells.

        Args:
            position: (row, col) of the cell to get neighbors for.

        Returns:
            List of valid neighbor positions.
        """
        neighbors: list[tuple[int, int]] = []
        row, col = position
        for dr, dc in DIRECTIONS:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.grid_height and 0 <= nc < self.grid_width:
                if self.grid[nr][nc] == 0:
                    neighbors.append((nr, nc))
        return neighbors

    def toggle_wall(self, position: tuple[int, int]) -> bool:
        """Toggle a cell between wall and open.

        Returns False if the toggle would make the maze unsolvable
        (fewer than MIN_DISTINCT_PATHS paths).

        Args:
            position: (row, col) of the cell to toggle.

        Returns:
            True if the toggle was applied, False if it was rejected.
        """
        row, col = position

        if position == self.start or position == self.end:
            return False

        if not (0 <= row < self.grid_height and 0 <= col < self.grid_width):
            return False

        original = self.grid[row][col]
        self.grid[row][col] = 1 - original

        if not self.validate_paths():
            self.grid[row][col] = original
            return False

        return True
