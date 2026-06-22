""" get the hexadecimal representation in a file """
from pathlib import Path
from .cell import Cell
from .errors import MazeWriteError


def maze_to_hex_lines(grid: list[list[Cell]]) -> list[str]:
    """Convert a maze grid to hexadecimal lines."""
    return [
        "".join(cell.to_hexa() for cell in row)
        for row in grid
    ]


def write_maze_file(
    grid: list[list[Cell]],
    output_file: str,
    entry: tuple[int, int],
    exit_: tuple[int, int],
    path: str,
) -> None:
    """Write the maze, entry, exit and shortest path to a file."""
    output_path = Path(output_file)

    lines = maze_to_hex_lines(grid)

    try:
        with output_path.open("w", encoding="utf-8") as file:
            for line in lines:
                file.write(f"{line}\n")

            file.write("\n")
            file.write(f"{entry[0]},{entry[1]}\n")
            file.write(f"{exit_[0]},{exit_[1]}\n")
            file.write(f"{path}\n")
    except PermissionError as error:
        raise MazeWriteError(
            f"Permission denied while writing: {output_file}"
        ) from error

    except IsADirectoryError as error:
        raise MazeWriteError(
            f"Expected output file but got directory: {output_file}"
        ) from error

    except OSError as error:
        raise MazeWriteError(
            f"Unable to write output file '{output_file}': {error}"
        ) from error
