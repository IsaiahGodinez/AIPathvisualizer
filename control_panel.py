"""ControlPanel class for the right-side UI sidebar."""

import pygame

from constants import (
    ALGORITHM_A_STAR,
    ALGORITHM_GREEDY_BFS,
    ALGORITHM_UCS,
    ALGORITHM_BFS,
    ALGORITHM_DFS,
    COLOR_PANEL_BG,
    COLOR_BUTTON,
    COLOR_BUTTON_HOVER,
    COLOR_BUTTON_TEXT,
    COLOR_TEXT,
    COLOR_SELECTED,
    DEFAULT_GRID_WIDTH,
    PANEL_WIDTH,
)


class ControlPanel:
    """Draws and manages the right-side UI panel."""

    def __init__(self, panel_x: int, panel_height: int):
        """Set up fonts, default settings, and compute UI layout."""
        self.panel_x = panel_x
        self.panel_height = panel_height
        self.grid_size: int = DEFAULT_GRID_WIDTH
        self.algorithm: str = ALGORITHM_A_STAR
        self.speed: int = 15  # Steps per second

        self._font = pygame.font.SysFont("consolas", 16)
        self._font_small = pygame.font.SysFont("consolas", 13)
        self._font_title = pygame.font.SysFont("consolas", 18, bold=True)
        self._metrics: dict | None = None
        self._dragging_speed = False
        self._dragging_grid_size = False

        self._build_layout()

    def _build_layout(self) -> None:
        """Compute positions and rects for all UI elements."""
        x = self.panel_x + 15
        w = PANEL_WIDTH - 30
        y = 15

        # Title
        self._title_y = y
        y += 35

        # Algorithm selector
        self._algo_label_y = y
        y += 22
        self._algo_buttons: list[tuple[pygame.Rect, str, str]] = []
        algo_items = [
            (ALGORITHM_A_STAR, "A*"),
            (ALGORITHM_GREEDY_BFS, "Greedy BFS"),
            (ALGORITHM_UCS, "UCS"),
            (ALGORITHM_BFS, "BFS"),
            (ALGORITHM_DFS, "DFS"),
        ]
        for algo_key, algo_label in algo_items:
            rect = pygame.Rect(x, y, w, 28)
            self._algo_buttons.append((rect, algo_key, algo_label))
            y += 32

        y += 10

        # Speed slider
        self._speed_label_y = y
        y += 22
        self._speed_slider_rect = pygame.Rect(x, y, w, 20)
        y += 30

        # Grid size slider
        self._grid_size_label_y = y
        y += 22
        self._grid_size_slider_rect = pygame.Rect(x, y, w, 20)
        y += 35

        # Action buttons
        self._action_buttons: list[tuple[pygame.Rect, str, str]] = []
        button_defs = [
            ("start", "Start"),
            ("pause", "Pause"),
            ("reset", "Reset"),
            ("generate", "Generate New"),
            ("clear_walls", "Clear Walls"),
        ]
        for action, label in button_defs:
            rect = pygame.Rect(x, y, w, 32)
            self._action_buttons.append((rect, action, label))
            y += 38

        y += 10

        # Metrics area
        self._metrics_y = y

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the full panel: background, buttons, sliders, and metrics."""
        panel_rect = pygame.Rect(self.panel_x, 0, PANEL_WIDTH, self.panel_height)
        pygame.draw.rect(screen, COLOR_PANEL_BG, panel_rect)

        x = self.panel_x + 15

        title = self._font_title.render("Pathfinder", True, COLOR_TEXT)
        screen.blit(title, (x, self._title_y))

        label = self._font.render("Algorithm", True, COLOR_TEXT)
        screen.blit(label, (x, self._algo_label_y))

        mouse_pos = pygame.mouse.get_pos()

        for rect, algo_key, algo_label in self._algo_buttons:
            is_selected = self.algorithm == algo_key
            is_hover = rect.collidepoint(mouse_pos)
            if is_selected:
                color = COLOR_SELECTED
            elif is_hover:
                color = COLOR_BUTTON_HOVER
            else:
                color = COLOR_BUTTON
            pygame.draw.rect(screen, color, rect, border_radius=4)
            text = self._font.render(algo_label, True, COLOR_BUTTON_TEXT)
            screen.blit(text, (rect.x + 10, rect.y + 5))

        # Speed slider
        label = self._font.render(f"Speed: {self.speed} steps/s", True, COLOR_TEXT)
        screen.blit(label, (x, self._speed_label_y))
        self._draw_slider(screen, self._speed_slider_rect,
                          (self.speed - 1) / 59)  # 1-60 range

        # Grid size slider
        label = self._font.render(f"Grid: {self.grid_size}x{self.grid_size}",
                                  True, COLOR_TEXT)
        screen.blit(label, (x, self._grid_size_label_y))
        self._draw_slider(screen, self._grid_size_slider_rect,
                          (self.grid_size - 5) / 45)  # 5-50 range

        # Action buttons
        for rect, action, btn_label in self._action_buttons:
            is_hover = rect.collidepoint(mouse_pos)
            color = COLOR_BUTTON_HOVER if is_hover else COLOR_BUTTON
            pygame.draw.rect(screen, color, rect, border_radius=4)
            text = self._font.render(btn_label, True, COLOR_BUTTON_TEXT)
            screen.blit(text, (rect.x + 10, rect.y + 7))

        self._draw_metrics_area(screen)

    def _draw_slider(self, screen: pygame.Surface, rect: pygame.Rect,
                     value: float) -> None:
        """Draw a horizontal slider with a knob at the given normalized value (0–1)."""
        value = max(0.0, min(1.0, value))
        # Track
        pygame.draw.rect(screen, COLOR_BUTTON, rect, border_radius=4)
        # Fill
        fill_w = int(rect.width * value)
        if fill_w > 0:
            fill_rect = pygame.Rect(rect.x, rect.y, fill_w, rect.height)
            pygame.draw.rect(screen, COLOR_SELECTED, fill_rect, border_radius=4)
        # Knob
        knob_x = rect.x + fill_w
        knob_rect = pygame.Rect(knob_x - 4, rect.y - 2, 8, rect.height + 4)
        pygame.draw.rect(screen, COLOR_TEXT, knob_rect, border_radius=3)

    def _draw_metrics_area(self, screen: pygame.Surface) -> None:
        """Draw the metrics section with current algorithm stats."""
        x = self.panel_x + 15
        y = self._metrics_y

        header = self._font.render("-- Metrics --", True, COLOR_TEXT)
        screen.blit(header, (x, y))
        y += 25

        if self._metrics:
            lines = [
                f"Path cost:  {self._metrics.get('path_cost', '-')}",
                f"Explored:   {self._metrics.get('nodes_explored', '-')}",
                f"Time:       {self._metrics.get('time_elapsed', 0):.4f}s",
            ]
        else:
            lines = [
                "Path cost:  -",
                "Explored:   -",
                "Time:       -",
            ]

        for line in lines:
            text = self._font_small.render(line, True, COLOR_TEXT)
            screen.blit(text, (x, y))
            y += 20

    def handle_input(self, event: pygame.event.Event) -> str | None:
        """Process a click or drag on the panel; return an action string or None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Algorithm selector
            for rect, algo_key, _ in self._algo_buttons:
                if rect.collidepoint(pos):
                    self.algorithm = algo_key
                    return None

            # Speed slider
            if self._speed_slider_rect.collidepoint(pos):
                self._dragging_speed = True
                self._update_speed_from_mouse(pos[0])
                return None

            # Grid size slider
            if self._grid_size_slider_rect.collidepoint(pos):
                self._dragging_grid_size = True
                self._update_grid_size_from_mouse(pos[0])
                return None

            # Action buttons
            for rect, action, _ in self._action_buttons:
                if rect.collidepoint(pos):
                    return action

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging_speed = False
            self._dragging_grid_size = False

        elif event.type == pygame.MOUSEMOTION:
            if self._dragging_speed:
                self._update_speed_from_mouse(event.pos[0])
            if self._dragging_grid_size:
                self._update_grid_size_from_mouse(event.pos[0])

        return None

    def _update_speed_from_mouse(self, mouse_x: int) -> None:
        """Update speed from slider mouse position."""
        rect = self._speed_slider_rect
        ratio = (mouse_x - rect.x) / rect.width
        ratio = max(0.0, min(1.0, ratio))
        self.speed = int(1 + ratio * 59)  # 1-60

    def _update_grid_size_from_mouse(self, mouse_x: int) -> None:
        """Update grid size from slider mouse position."""
        rect = self._grid_size_slider_rect
        ratio = (mouse_x - rect.x) / rect.width
        ratio = max(0.0, min(1.0, ratio))
        self.grid_size = int(5 + ratio * 45)  # 5-50

    def get_settings(self) -> dict:
        """Return the current algorithm, grid size, and speed settings."""
        return {
            "grid_size": self.grid_size,
            "algorithm": self.algorithm,
            "speed": self.speed,
        }

    def draw_metrics(self, metrics: dict) -> None:
        """Store metrics dict for display in the next draw call."""
        self._metrics = metrics
