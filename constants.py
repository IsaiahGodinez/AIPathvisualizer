"""Shared constants for the pathfinding visualizer."""

# Grid defaults
DEFAULT_GRID_WIDTH = 25
DEFAULT_GRID_HEIGHT = 25
# Movement directions (4-directional only, no diagonals)
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right

# Algorithm names
ALGORITHM_A_STAR = "a_star"
ALGORITHM_GREEDY_BFS = "greedy_bfs"
ALGORITHM_UCS = "ucs"
ALGORITHM_BFS = "bfs"
ALGORITHM_DFS = "dfs"

# Validation
MAX_GENERATION_RETRIES = 100
MIN_DISTINCT_PATHS = 3

# Colors (RGB)
COLOR_BACKGROUND = (240, 240, 240)
COLOR_GRID_LINE = (200, 200, 200)
COLOR_EMPTY = (255, 255, 255)
COLOR_WALL = (40, 40, 40)
COLOR_START = (0, 200, 0)
COLOR_END = (200, 0, 0)
COLOR_FRONTIER = (135, 206, 250)    # Light blue
COLOR_EXPLORED = (255, 235, 156)    # Pale yellow
COLOR_PATH = (255, 215, 0)          # Gold
COLOR_PANEL_BG = (50, 50, 50)
COLOR_BUTTON = (80, 80, 80)
COLOR_BUTTON_HOVER = (100, 100, 100)
COLOR_BUTTON_TEXT = (255, 255, 255)
COLOR_TEXT = (220, 220, 220)
COLOR_SELECTED = (100, 180, 255)

# Window
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
PANEL_WIDTH = 230
FPS = 60
