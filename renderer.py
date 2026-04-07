"""Renderer class handling all Pygame drawing for the grid area."""

import pygame

from constants import (
    COLOR_BACKGROUND,
    COLOR_GRID_LINE,
    COLOR_EMPTY,
    COLOR_WALL,
    COLOR_START,
    COLOR_END,
    COLOR_FRONTIER,
    COLOR_EXPLORED,
    COLOR_PATH,
    PANEL_WIDTH,
)


class Renderer:
    """Draws the grid area each frame without modifying game state."""

    def __init__(self, screen: pygame.Surface, grid: list[list[int]],
                 start: tuple[int, int], end: tuple[int, int]):
        """Set up drawing state and compute initial cell size."""
        self.screen = screen
        self.grid = grid
        self.start = start
        self.end = end
        self.path: list[tuple[int, int]] = []
        self.open_set: set[tuple[int, int]] = set()
        self.closed_set: set[tuple[int, int]] = set()
        self.cell_size = self._compute_cell_size()

    def _compute_cell_size(self) -> int:
        """Calculate cell pixel size to fit the grid in the available area."""
        if not self.grid or not self.grid[0]:
            return 20
        available_width = self.screen.get_width() - PANEL_WIDTH
        available_height = self.screen.get_height()
        grid_height = len(self.grid)
        grid_width = len(self.grid[0])
        return min(available_width // grid_width, available_height // grid_height)

    def set_grid(self, grid: list[list[int]], start: tuple[int, int],
                 end: tuple[int, int]) -> None:
        """Update the grid reference and recalculate cell size."""
        self.grid = grid
        self.start = start
        self.end = end
        self.cell_size = self._compute_cell_size()

    def draw_grid(self) -> None:
        """Draw all cells with appropriate colors and grid lines."""
        grid_height = len(self.grid)
        grid_width = len(self.grid[0]) if self.grid else 0
        path_set = set(self.path)

        grid_pixel_w = grid_width * self.cell_size
        grid_pixel_h = grid_height * self.cell_size
        pygame.draw.rect(self.screen, COLOR_BACKGROUND,
                         (0, 0, grid_pixel_w, grid_pixel_h))

        for row in range(grid_height):
            for col in range(grid_width):
                x = col * self.cell_size
                y = row * self.cell_size
                pos = (row, col)
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

                if pos == self.start:
                    color = COLOR_START
                elif pos == self.end:
                    color = COLOR_END
                elif pos in path_set:
                    color = COLOR_PATH
                elif self.grid[row][col] == 1:
                    color = COLOR_WALL
                elif pos in self.closed_set:
                    color = COLOR_EXPLORED
                elif pos in self.open_set:
                    color = COLOR_FRONTIER
                else:
                    color = COLOR_EMPTY

                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, COLOR_GRID_LINE, rect, 1)

    def draw_path(self) -> None:
        """Draw final path cells, skipping start and end."""
        for pos in self.path:
            if pos == self.start or pos == self.end:
                continue
            row, col = pos
            x = col * self.cell_size
            y = row * self.cell_size
            rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
            pygame.draw.rect(self.screen, COLOR_PATH, rect)
            pygame.draw.rect(self.screen, COLOR_GRID_LINE, rect, 1)

    def draw_explored(self) -> None:
        """Draw explored (yellow) and frontier (blue) cells on the grid."""
        path_set = set(self.path)

        for pos in self.closed_set:
            if pos in (self.start, self.end) or pos in path_set:
                continue
            row, col = pos
            x = col * self.cell_size
            y = row * self.cell_size
            rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
            pygame.draw.rect(self.screen, COLOR_EXPLORED, rect)
            pygame.draw.rect(self.screen, COLOR_GRID_LINE, rect, 1)

        for pos in self.open_set:
            if pos in (self.start, self.end) or pos in path_set:
                continue
            if pos in self.closed_set:
                continue
            row, col = pos
            x = col * self.cell_size
            y = row * self.cell_size
            rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
            pygame.draw.rect(self.screen, COLOR_FRONTIER, rect)
            pygame.draw.rect(self.screen, COLOR_GRID_LINE, rect, 1)

    def update(self) -> None:
        """Draw the complete grid area. Called each frame by the App."""
        self.draw_grid()

    def pixel_to_grid(self, pixel_x: int, pixel_y: int) -> tuple[int, int] | None:
        """Convert pixel coordinates to (row, col), or None if outside the grid."""
        if not self.grid or not self.grid[0]:
            return None
        grid_height = len(self.grid)
        grid_width = len(self.grid[0])
        col = pixel_x // self.cell_size
        row = pixel_y // self.cell_size
        if 0 <= row < grid_height and 0 <= col < grid_width:
            return (row, col)
        return None
