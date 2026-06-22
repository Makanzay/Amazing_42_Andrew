"""Solve mazes using graph traversal algorithms."""

from collections import deque
from .cell import Cell


def get_open_neighbours(
    grid: list[list[Cell]],
    cell: Cell,
) -> list[tuple[Cell, str]]:
    """Return reachable neighbours and their direction from a cell."""
    height = len(grid)
    width = len(grid[0])
    neighbours: list[tuple[Cell, str]] = []

    x = cell.x
    y = cell.y

    if not cell.north and y > 0 and not grid[y - 1][x].blocked:
        neighbours.append((grid[y - 1][x], "N"))
    if not cell.east and x < width - 1 and not grid[y][x + 1].blocked:
        neighbours.append((grid[y][x + 1], "E"))
    if not cell.south and y < height - 1 and not grid[y + 1][x].blocked:
        neighbours.append((grid[y + 1][x], "S"))
    if not cell.west and x > 0 and not grid[y][x - 1].blocked:
        neighbours.append((grid[y][x - 1], "W"))

    return neighbours


def solve_shortest_path(
    grid: list[list[Cell]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
) -> str:
    """Return the shortest path from entry to exit using BFS
    each path are stored with the cell ,so each time you go to 
    the next one you add to the cell position the path to it"""
    start = grid[entry[1]][entry[0]]
    target = grid[exit_[1]][exit_[0]]

    if start.blocked or target.blocked:
        raise ValueError("Entry or exit cannot be inside the 42 pattern")

    queue: deque[tuple[Cell, str]] = deque()
    queue.append((start, ""))

    visited: set[tuple[int, int]] = {(start.x, start.y)}

    while queue:
        current, path = queue.popleft()

        if current == target:
            return path

        for neighbour, direction in get_open_neighbours(grid, current):
            position = (neighbour.x, neighbour.y)

            if position not in visited:
                visited.add(position)
                queue.append((neighbour, path + direction))

    raise ValueError("No path found from entry to exit")
