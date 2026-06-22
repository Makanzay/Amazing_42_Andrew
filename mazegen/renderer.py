"""Render mazes in ASCII format."""

from .cell import Cell


def render_ascii(
    grid: list[list[Cell]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
) -> str:
    """Return an ASCII representation of the maze."""
    lines: list[str] = []

    for row in grid:
        top_line = ""
        middle_line = ""

        for cell in row:
            top_line += "+"
            top_line += "---" if cell.north else "   "

            middle_line += "|" if cell.west else " "

            if (cell.x, cell.y) == entry:
                middle_line += " S "
            elif (cell.x, cell.y) == exit_:
                middle_line += " E "
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
