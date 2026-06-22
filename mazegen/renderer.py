"""Render mazes in ASCII format."""

from .cell import Cell


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
) -> str:
    """Return an ASCII representation of the maze."""
    lines: list[str] = []

    path_positions = path_to_positions(entry, path) if path else set()

    for row in grid:
        top_line = ""
        middle_line = ""

        for cell in row:
            top_line += "+"
            top_line += "---" if cell.north else "   "

            middle_line += "|" if cell.west else " "

            if cell.blocked:
                middle_line += " # "
            elif (cell.x, cell.y) == entry:
                middle_line += " S "
            elif (cell.x, cell.y) == exit_:
                middle_line += " E "
            elif (cell.x, cell.y) in path_positions:
                middle_line += " . "
            else:
                middle_line += "   "

        top_line += "+"
        middle_line += "|" if row[-1].east else " "

        lines.append(top_line)
        lines.append(middle_line)

    bottom_line = ""

    for cell in grid[-1]:
        bottom_line += "+"
        bottom_line += "---" if cell.south else "   "

    bottom_line += "+"
    lines.append(bottom_line)

    return "\n".join(lines)


def render_mlx()