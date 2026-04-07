"""App class — main game loop wiring together all components."""

import pygame

from map_generator import MapGenerator
from agent import Agent
from renderer import Renderer
from control_panel import ControlPanel
from constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    PANEL_WIDTH,
    FPS,
    COLOR_BACKGROUND,
    ALGORITHM_BFS,
    ALGORITHM_DFS,
)


class App:
    """Main game loop tying together MapGenerator, Agent, Renderer, and ControlPanel."""

    def __init__(self):
        """Initialize Pygame, create the window, and set up all components."""
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pathfinding Visualizer")
        self.clock = pygame.time.Clock()

        # Control panel (right side)
        panel_x = WINDOW_WIDTH - PANEL_WIDTH
        self.control_panel = ControlPanel(panel_x, WINDOW_HEIGHT)

        # Map generator
        settings = self.control_panel.get_settings()
        self.map_generator = MapGenerator(
            grid_width=settings["grid_size"],
            grid_height=settings["grid_size"],
        )

        # Renderer
        self.renderer = Renderer(
            self.screen,
            self.map_generator.grid,
            self.map_generator.start,
            self.map_generator.end,
        )

        # Agent
        self.agent = Agent(
            self.map_generator.grid,
            self.map_generator.start,
            self.map_generator.end,
        )

        # State
        self.is_running = False
        self.is_paused = False
        self._step_accumulator = 0.0  # ms accumulated for time-based stepping
        self._running = True

    def run(self) -> None:
        """Main Pygame game loop: handle events, update state, draw."""
        while self._running:
            dt = self.clock.tick(FPS)  # ms since last frame
            self._handle_events()
            self._update(dt)
            self._draw()

        pygame.quit()

    def _handle_events(self) -> None:
        """Process all Pygame events for this frame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
                return

            # Pass all relevant events to control panel (clicks + drags)
            action = self.control_panel.handle_input(event)
            if action:
                self._handle_action(action)
                continue

            # Grid click — toggle walls (only when not running)
            if (event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and not self.is_running):
                grid_pos = self.renderer.pixel_to_grid(event.pos[0],
                                                       event.pos[1])
                if grid_pos:
                    self.map_generator.toggle_wall(grid_pos)

    def _handle_action(self, action: str) -> None:
        """Dispatch a control panel action string to the appropriate handler."""
        if action == "start":
            if self.agent.is_complete:
                self.reset()
            self.start_algorithm()

        elif action == "pause":
            self.is_paused = not self.is_paused

        elif action == "reset":
            self.reset()

        elif action == "generate":
            self._generate_new_maze()

        elif action == "clear_walls":
            self._clear_walls()

    def start_algorithm(self) -> None:
        """Initialize the Agent with the selected algorithm and start."""
        settings = self.control_panel.get_settings()
        self.agent = Agent(
            self.map_generator.grid,
            self.map_generator.start,
            self.map_generator.end,
        )
        self.agent.start_algorithm(settings["algorithm"])
        self.is_running = True
        self.is_paused = False
        self._step_accumulator = 0.0
        self.renderer.path = []
        self.renderer.open_set = set()
        self.renderer.closed_set = set()
        self.control_panel.draw_metrics(None)

    def reset(self) -> None:
        """Reset the agent and clear visualization, keeping the current grid."""
        self.agent.reset()
        self.is_running = False
        self.is_paused = False
        self._step_accumulator = 0.0
        self.renderer.path = []
        self.renderer.open_set = set()
        self.renderer.closed_set = set()
        self.control_panel.draw_metrics(None)

    def _generate_new_maze(self) -> None:
        """Create a new MapGenerator with current settings and reset."""
        settings = self.control_panel.get_settings()
        self.map_generator = MapGenerator(
            grid_width=settings["grid_size"],
            grid_height=settings["grid_size"],
        )
        self.renderer.set_grid(
            self.map_generator.grid,
            self.map_generator.start,
            self.map_generator.end,
        )
        self.reset()

    def _clear_walls(self) -> None:
        """Set all wall cells to open, keeping start/end."""
        for row in range(self.map_generator.grid_height):
            for col in range(self.map_generator.grid_width):
                self.map_generator.grid[row][col] = 0
        self.map_generator.grid[self.map_generator.start[0]][
            self.map_generator.start[1]] = 0
        self.map_generator.grid[self.map_generator.end[0]][
            self.map_generator.end[1]] = 0
        self.reset()

    def _update(self, dt: float) -> None:
        """Step the algorithm based on elapsed time (dt in ms)."""
        if not self.is_running or self.is_paused:
            return

        if self.agent.is_complete:
            self.is_running = False
            self.renderer.path = self.agent.path
            self.control_panel.draw_metrics(self.agent.get_metrics())
            return

        speed = self.control_panel.speed
        step_interval = 1000.0 / speed  # ms per step

        self._step_accumulator += dt

        while self._step_accumulator >= step_interval and not self.agent.is_complete:
            self._step_accumulator -= step_interval
            self.agent.step()

        # Update renderer with current agent state
        self.renderer.closed_set = set(self.agent.explored_order)
        if self.agent._algorithm in (ALGORITHM_BFS, ALGORITHM_DFS):
            # BFS/DFS store raw Node objects in open_set
            self.renderer.open_set = {
                item.position for item in self.agent.open_set
            }
        else:
            # A*, Greedy BFS, UCS store (priority, counter, Node) tuples
            self.renderer.open_set = {
                item[2].position for item in self.agent.open_set
            }

        if self.agent.is_complete:
            self.is_running = False
            self.renderer.path = self.agent.path
            self.control_panel.draw_metrics(self.agent.get_metrics())

    def _draw(self) -> None:
        """Draw everything to the screen."""
        self.screen.fill(COLOR_BACKGROUND)
        self.renderer.update()
        self.control_panel.draw(self.screen)
        pygame.display.flip()
