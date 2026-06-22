"""Render mazes in ASCII format."""

from .cell import Cell

ANSI_COLORS = {
    "white": "\033[97m",
    "red": "\033[91m",
    "green": "\033[92m",
    "blue": "\033[94m",
    "yellow": "\033[93m",
    "cyan": "\033[96m",
    "magenta": "\033[95m",
    "gray": "\033[90m",
}
ANSI_RESET = "\033[0m"


def color_text(text: str, color: str, use_color: bool) -> str:
    """Return text wrapped in ANSI colour codes when enabled."""
    if not use_color:
        return text
    return f"{ANSI_COLORS[color]}{text}{ANSI_RESET}"


def path_to_positions(
    entry: tuple[int, int],
    path: str,
) -> set[tuple[int, int]]:
    """Convert a path string into maze coordinates"""
    x, y = entry
    positions: set[tuple[int, int]] = {(x, y)}

    for move in path:
        if move == "N":
            y -= 1
        elif move == "E":
            x += 1
        elif move == "S":
            y += 1
        elif move == "W":
            x -= 1

        positions.add((x, y))

    return positions


def render_ascii(
    grid: list[list[Cell]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
    path: str = "",
    wall_color: str = "white",
    path_color: str = "yellow",
    pattern_color: str = "blue",
    use_color: bool = True,
) -> str:
    """Return an ASCII representation of the maze."""
    lines: list[str] = []

    path_positions = path_to_positions(entry, path) if path else set()

    for row in grid:
        top_line = ""
        middle_line = ""

        for cell in row:
            top_line += color_text("+", wall_color, use_color)
            top_line += (
                color_text("---", wall_color, use_color)
                if cell.north else "   "
            )

            middle_line += (
                color_text("|", wall_color, use_color)
                if cell.west else " "
            )

            if cell.blocked:
                middle_line += color_text(" # ", pattern_color, use_color)
            elif (cell.x, cell.y) == entry:
                middle_line += color_text(" S ", "green", use_color)
            elif (cell.x, cell.y) == exit_:
                middle_line += color_text(" E ", "red", use_color)
            elif (cell.x, cell.y) in path_positions:
                middle_line += color_text(" . ", path_color, use_color)
            else:
                middle_line += "   "

        top_line += color_text("+", wall_color, use_color)
        middle_line += (
            color_text("|", wall_color, use_color)
            if row[-1].east else " "
        )

        lines.append(top_line)
        lines.append(middle_line)

    bottom_line = ""

    for cell in grid[-1]:
        bottom_line += color_text("+", wall_color, use_color)
        bottom_line += (
            color_text("---", wall_color, use_color)
            if cell.south else "   "
        )

    bottom_line += color_text("+", wall_color, use_color)
    lines.append(bottom_line)

    return "\n".join(lines)
