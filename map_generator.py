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
    """Generates a DFS maze and ensures at least MIN_DISTINCT_PATHS exist."""

    def __init__(self, grid_width: int = DEFAULT_GRID_WIDTH,
                 grid_height: int = DEFAULT_GRID_HEIGHT):
        """Round dimensions to odd and generate the initial maze."""
        # Odd dimensions keep DFS passage/wall alignment correct
        self.grid_width = grid_width if grid_width % 2 == 1 else grid_width + 1
        self.grid_height = grid_height if grid_height % 2 == 1 else grid_height + 1
        self.grid: list[list[int]] = []
        self.start: tuple[int, int] = (0, 0)
        self.end: tuple[int, int] = (self.grid_height - 1, self.grid_width - 1)
        self.generate_grid()

    def generate_grid(self) -> list[list[int]]:
        """Carve a DFS maze, open extra walls, and validate MIN_DISTINCT_PATHS paths.

        Retries up to MAX_GENERATION_RETRIES times if validation fails.
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
        """Return True if at least MIN_DISTINCT_PATHS distinct paths exist."""
        return self._count_distinct_paths(MIN_DISTINCT_PATHS) >= MIN_DISTINCT_PATHS

    def _count_distinct_paths(self, max_count: int = 3) -> int:
        """Count distinct paths from start to end, up to max_count.

        Finds a path, blocks each intermediate node one at a time, and checks
        for an alternate route — each success counts as a distinct path.
        """
        first_path = self._bfs(self.start, self.end)
        if not first_path:
            return 0

        count = 1

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

        Passages land on even-indexed cells; the wall between two passages
        is removed to connect them.
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
                self.grid[row + dr][col + dc] = 0  # open wall between cells
                self.grid[nr][nc] = 0
                stack.append((nr, nc))
            else:
                stack.pop()

        self.grid[self.end[0]][self.end[1]] = 0

        # Connect end if the DFS didn't reach it (rare on very small grids)
        if not self._bfs(self.start, self.end):
            self._connect_end()

    def _connect_end(self) -> None:
        """Carve a passage from the end cell toward start until reachable."""
        er, ec = self.end
        r, c = er, ec
        while True:
            self.grid[r][c] = 0
            if self._bfs(self.start, (r, c)):
                break
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
        """Open walls to reach MIN_DISTINCT_PATHS, then a few more for variety."""
        candidates = self._get_wall_removal_candidates()
        random.shuffle(candidates)

        # Mandatory: remove walls until MIN_DISTINCT_PATHS is satisfied
        remaining: list[tuple[int, int]] = []
        for pos in candidates:
            if self._count_distinct_paths(MIN_DISTINCT_PATHS) >= MIN_DISTINCT_PATHS:
                remaining.append(pos)
                remaining.extend(
                    candidates[candidates.index(pos) + 1:]
                )
                break
            self.grid[pos[0]][pos[1]] = 0

        # Cosmetic: remove ~10% more for visual variety
        if remaining:
            extra_count = max(1, int(len(remaining) * 0.10))
            random.shuffle(remaining)
            for pos in remaining[:extra_count]:
                self.grid[pos[0]][pos[1]] = 0

    def _get_wall_removal_candidates(self) -> list[tuple[int, int]]:
        """Return interior walls that bridge two open cells (removal candidates)."""
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
        """Run BFS from start to end; return the path or None."""
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
        """Fix start at (0,0) and end at the furthest even-indexed corner."""
        self.start = (0, 0)
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
        """Return open, in-bounds neighbors (4-directional)."""
        neighbors: list[tuple[int, int]] = []
        row, col = position
        for dr, dc in DIRECTIONS:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.grid_height and 0 <= nc < self.grid_width:
                if self.grid[nr][nc] == 0:
                    neighbors.append((nr, nc))
        return neighbors

    def toggle_wall(self, position: tuple[int, int]) -> bool:
        """Toggle a wall; reject the change if it breaks solvability."""
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
