"""rendering with mlx"""

import signal
from collections.abc import Callable

from mlx import Mlx
from .cell import Cell
from .renderer import path_to_positions


CELL_SIZE = 24

COLOR_WALL = 0xFFFFFF     # white for walls
COLOR_START = 0x00FF00    # Green for start
COLOR_EXIT = 0xFF0000     # Red the end
COLOR_BLOCKED = 0x4444FF  # blue for the logo
COLOR_FLOOR = 0x111111    # grey for the cell
COLOR_PATH = 0x00FFFF

MLX_COLORS = {
    "white": 0xFFFFFF,
    "red": 0xFF0000,
    "green": 0x00FF00,
    "blue": 0x4444FF,
    "yellow": 0x00FFFF,
    "cyan": 0xFFFF00,
    "magenta": 0xFF00FF,
    "gray": 0x888888,
}

ESCAPE_KEY = 65307
KEY_C = 99
KEY_P = 112
KEY_Q = 113
KEY_R = 114

RegenerateCallback = Callable[[], tuple[list[list[Cell]], str]]


class MlxRenderer:
    """Display a maze using MiniLibX."""

    def __init__(
        self,
        grid: list[list[Cell]],
        entry: tuple[int, int],
        exit_: tuple[int, int],
        path: str = "",
        show_path: bool = True,
        wall_color: str = "white",
        path_color: str = "yellow",
        pattern_color: str = "blue",
        regenerate_callback: RegenerateCallback | None = None,
    ) -> None:
        self.grid = grid
        self.entry = entry
        self.exit = exit_
        self.path = path
        self.show_path = show_path
        self.wall_color_name = wall_color
        self.path_color_name = path_color
        self.pattern_color_name = pattern_color
        self.regenerate_callback = regenerate_callback
        self.wall_color_choices = list(MLX_COLORS)

        self.width = len(grid[0]) * CELL_SIZE + 1
        self.height = len(grid) * CELL_SIZE + 1

        self.mlx_loader = Mlx()
        self.mlx_ptr = self.mlx_loader.mlx_init()
        self.closed = False
        self.cleaned_up = False

        if not self.mlx_ptr:
            raise RuntimeError("mlx_init failed")

        self.win_ptr = self.mlx_loader.mlx_new_window(
            self.mlx_ptr,
            self.width,
            self.height,
            "A-Maze-ing",
        )

        if not self.win_ptr:
            raise RuntimeError("mlx_new_window failed")

        self.img_ptr = self.mlx_loader.mlx_new_image(
                self.mlx_ptr,
                self.width,
                self.height,
            )

        if not self.img_ptr:
            raise RuntimeError("mlx_new_image failed")

        self.addr, self.bits_per_pixel, self.line_length, self.endian = (
            self.mlx_loader.mlx_get_data_addr(self.img_ptr)
        )

    def draw_vertical_line(
            self, x: int, y1: int, y2: int, color: int) -> None:
        """Draw a single-pixel wide vertical line"""
        for y in range(y1, y2 + 1):
            self.put_pixel(
                x, y, color)

    def draw_horizontal_line(
            self, x1: int, x2: int, y: int, color: int) -> None:
        """Draw a single-pixel wide horizontal line"""
        for x in range(x1, x2 + 1):
            self.put_pixel(
                x, y, color)

    def draw_cell_background(
            self, x: int, y: int, size: int, color: int) -> None:
        """Fill the interior of a cell with a plain color."""
        for py in range(y, y + size):
            for px in range(x, x + size):
                self.put_pixel(px, py, color)

    def render(self, param: object | None = None) -> int:
        """Iterate through grid to draw floors, special states, and walls
        --------------------------------------------------------------
        x_idx & y_idx relative position"""
        if self.closed:
            return 0

        for y_idx, row in enumerate(self.grid):
            for x_idx, cell in enumerate(self.grid[y_idx]):
                screen_x = x_idx * CELL_SIZE
                screen_y = y_idx * CELL_SIZE

                if getattr(cell, "blocked", False):
                    bg_color = self.get_color(
                        self.pattern_color_name, COLOR_BLOCKED)
                elif (cell.x, cell.y) == self.entry:
                    bg_color = COLOR_START
                elif (cell.x, cell.y) == self.exit:
                    bg_color = COLOR_EXIT
                elif self.is_path_cell(cell.x, cell.y):
                    bg_color = self.get_color(self.path_color_name, COLOR_PATH)
                else:
                    bg_color = COLOR_FLOOR

                self.draw_cell_background(
                    screen_x, screen_y, CELL_SIZE, bg_color)

                if cell.north:
                    self.draw_horizontal_line(
                        screen_x, screen_x + CELL_SIZE, screen_y,
                        self.get_color(self.wall_color_name, COLOR_WALL))
                if cell.east:
                    self.draw_vertical_line(
                        screen_x + CELL_SIZE, screen_y,
                        screen_y + CELL_SIZE,
                        self.get_color(self.wall_color_name, COLOR_WALL))
                if cell.south:
                    self.draw_horizontal_line(
                        screen_x, screen_x + CELL_SIZE,
                        screen_y + CELL_SIZE,
                        self.get_color(self.wall_color_name, COLOR_WALL))
                if cell.west:
                    self.draw_vertical_line(
                        screen_x, screen_y, screen_y + CELL_SIZE,
                        self.get_color(self.wall_color_name, COLOR_WALL))

        self.sync_image()
        self.mlx_loader.mlx_put_image_to_window(
            self.mlx_ptr,
            self.win_ptr,
            self.img_ptr,
            0,
            0,
        )
        self.sync_window()
        return 0

    def run(self) -> None:
        """Start the window event loop and draw the maze."""
        previous_sigint_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self.handle_sigint)

        self.mlx_loader.mlx_key_hook(
            self.win_ptr,
            self.handle_key,
            None,
        )
        self.mlx_loader.mlx_expose_hook(
            self.win_ptr,
            self.render,
            None,
        )
        self.mlx_loader.mlx_loop_hook(
            self.mlx_ptr,
            self.keep_alive,
            None,
        )
        self.render()
        try:
            self.mlx_loader.mlx_loop(self.mlx_ptr)
        finally:
            signal.signal(signal.SIGINT, previous_sigint_handler)
            self.cleanup()

    def close(self, param: object | None = None) -> int:
        """Ask MLX to stop the event loop."""
        if self.closed:
            return 0

        self.closed = True
        self.mlx_loader.mlx_loop_exit(self.mlx_ptr)
        return 0

    def handle_key(self, keycode: int, param: object | None = None) -> int:
        """Close the window when Escape is pressed."""
        if keycode in {ESCAPE_KEY, KEY_Q}:
            self.close()
        elif keycode == KEY_P:
            self.show_path = not self.show_path
            self.render()
        elif keycode == KEY_C:
            self.cycle_wall_color()
            self.render()
        elif keycode == KEY_R:
            self.regenerate()
            self.render()
        return 0

    def handle_sigint(self, signum: int, frame: object | None = None) -> None:
        """Close the MLX loop when Ctrl+C is pressed."""
        self.close()

    def keep_alive(self, param: object | None = None) -> int:
        """Keep Python callbacks active while MLX waits for events."""
        return 0

    def cleanup(self) -> None:
        """Destroy MLX resources after the event loop has stopped."""
        if self.cleaned_up:
            return

        self.cleaned_up = True
        self.mlx_loader.mlx_destroy_image(self.mlx_ptr, self.img_ptr)
        self.mlx_loader.mlx_destroy_window(self.mlx_ptr, self.win_ptr)

    def get_color(self, color_name: str, default: int) -> int:
        """Return an MLX colour value from a config name."""
        return MLX_COLORS.get(color_name, default)

    def is_path_cell(self, x: int, y: int) -> bool:
        """Return True when the cell belongs to the visible solution path."""
        if not self.show_path or not self.path:
            return False
        return (x, y) in path_to_positions(self.entry, self.path)

    def cycle_wall_color(self) -> None:
        """Cycle to the next configured wall colour."""
        current_index = self.wall_color_choices.index(self.wall_color_name)
        next_index = (current_index + 1) % len(self.wall_color_choices)
        self.wall_color_name = self.wall_color_choices[next_index]

    def regenerate(self) -> None:
        """Regenerate the maze when a callback is available."""
        if self.regenerate_callback is None:
            return
        self.grid, self.path = self.regenerate_callback()

    def sync_image(self) -> None:
        """Flush direct buffer writes before displaying the image."""
        sync_cmd = getattr(self.mlx_loader, "SYNC_IMAGE_WRITABLE", None)
        if sync_cmd is not None:
            self.mlx_loader.mlx_sync(self.mlx_ptr, sync_cmd, self.img_ptr)

    def sync_window(self) -> None:
        """Flush pending drawing commands to the window."""
        sync_cmd = getattr(self.mlx_loader, "SYNC_WIN_FLUSH", None)
        if sync_cmd is not None:
            self.mlx_loader.mlx_sync(self.mlx_ptr, sync_cmd, self.win_ptr)

    def put_pixel(self, x: int, y: int, color: int) -> None:
        """Write one pixel into the image buffer."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return

        bytes_per_pixel = self.bits_per_pixel // 8
        offset = y * self.line_length + x * bytes_per_pixel

        self.addr[offset] = color & 0xFF
        if bytes_per_pixel > 1:
            self.addr[offset + 1] = (color >> 8) & 0xFF
        if bytes_per_pixel > 2:
            self.addr[offset + 2] = (color >> 16) & 0xFF
        if bytes_per_pixel > 3:
            self.addr[offset + 3] = 0xFF
