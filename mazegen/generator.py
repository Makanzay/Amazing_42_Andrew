import random
import sys
from collections.abc import Callable

from .cell import Cell

ProgressCallback = Callable[[int, int, str], None]

PATTERN_42 = [
    "#   #  ### ",
    "#   # #   #",
    "#####    # ",
    "    #   #  ",
    "    # #####",
]


class MazeGenerator:
    """Generator of Maze by checking each cell"""

    def __init__(self, width: int, height: int,
                 seed: int | None = None) -> None:
        self.width = width
        self.height = height
        self.random = random.Random(seed)
        self.grid: list[list[Cell]] = self._create_grid(width, height)

    def _create_grid(self, width: int, height: int) -> list[list[Cell]]:
        """Built in method to generate our basic grid of cells"""
        return [[Cell(x, y) for x in range(width)] for y in range(height)]

    def reset_walls(self) -> None:
        """Reset non-blocked cells before running a generation algorithm."""
        for row in self.grid:
            for cell in row:
                if cell.blocked:
                    cell.north = True
                    cell.east = True
                    cell.south = True
                    cell.west = True
                    cell.visited = True
                else:
                    cell.north = True
                    cell.east = True
                    cell.south = True
                    cell.west = True
                    cell.visited = False

    def count_open_cells(self) -> int:
        """Return the number of non-blocked cells in the maze."""
        return sum(
            1
            for row in self.grid
            for cell in row
            if not cell.blocked
        )

    def _notify_progress(
        self,
        progress_callback: ProgressCallback | None,
        done: int,
        total: int,
        label: str,
    ) -> None:
        """Call a progress callback when one was supplied."""
        if progress_callback is not None:
            progress_callback(done, total, label)

    def remove_wall(self, current: Cell, neighbour: Cell) -> None:
        """Remove the wall between two adjacent cells."""
        dx = neighbour.x - current.x
        dy = neighbour.y - current.y

        if dx == 1 and dy == 0:
            current.east = False
            neighbour.west = False
        elif dx == -1 and dy == 0:
            current.west = False
            neighbour.east = False
        elif dx == 0 and dy == 1:
            current.south = False
            neighbour.north = False
        elif dx == 0 and dy == -1:
            current.north = False
            neighbour.south = False
        else:
            raise ValueError("Cells : are not adjacent")

    def get_cell(self, x: int, y: int) -> Cell:
        """Use the coordinates to access the right cell of the maze"""
        if not (0 <= x < self.width):
            raise IndexError(f"x coordinate out of bounds: {x}")

        if not (0 <= y < self.height):
            raise IndexError(f"y coordinate out of bounds: {y}")

        return self.grid[y][x]

    def get_neighbours(self, cell: Cell) -> list[Cell]:
        """find all the neighbours of a cell
        return it as a list of max four neighbours"""
        x: int = cell.x
        y: int = cell.y

        neighbours: list[Cell] = []

        if y > 0:
            neighbours.append(self.get_cell(x, y - 1))

        if x < self.width - 1:
            neighbours.append(self.get_cell(x + 1, y))

        if y < self.height - 1:
            neighbours.append(self.get_cell(x, y + 1))

        if x > 0:
            neighbours.append(self.get_cell(x - 1, y))

        return neighbours

    def get_unvisited_neighbours(self, cell: Cell) -> list[Cell]:
        """Neighbours that have not been visited yet."""
        return [
            neighbour
            for neighbour in self.get_neighbours(cell)
            if not neighbour.visited and not neighbour.blocked
        ]

    def generate_dfs(
        self,
        start_position: tuple[int, int] = (0, 0),
        progress_callback: ProgressCallback | None = None,
    ) -> None:
        """Generate a perfect maze using iterative dfs backtracking
        allow use to avoid recursive error on wide maze"""
        self.reset_walls()
        start = self.get_cell(start_position[0], start_position[1])

        if start.blocked:
            raise ValueError("Cant Start here cell is blocked")
        start.visited = True

        stack: list[Cell] = [start]
        visited_count = 1
        total_cells = self.count_open_cells()
        self._notify_progress(
            progress_callback, visited_count, total_cells, "dfs")

        while stack:
            current = stack[-1]
            unvisited = self.get_unvisited_neighbours(current)

            if unvisited:
                neighbour = self.random.choice(unvisited)
                self.remove_wall(current, neighbour)
                neighbour.visited = True
                visited_count += 1
                stack.append(neighbour)
                self._notify_progress(
                    progress_callback, visited_count, total_cells, "dfs")
            else:
                stack.pop()

    def generate_prim(
        self,
        start_position: tuple[int, int] = (0, 0),
        progress_callback: ProgressCallback | None = None,
    ) -> None:
        """Generate a perfect maze using randomized Prim's algorithm."""
        self.reset_walls()
        start = self.get_cell(start_position[0], start_position[1])

        if start.blocked:
            raise ValueError("Cant Start here cell is blocked")

        start.visited = True
        visited_count = 1
        total_cells = self.count_open_cells()
        frontiers: list[tuple[Cell, Cell]] = []

        for neighbour in self.get_unvisited_neighbours(start):
            frontiers.append((start, neighbour))

        self._notify_progress(
            progress_callback, visited_count, total_cells, "prim")

        while frontiers:
            index = self.random.randrange(len(frontiers))
            current, neighbour = frontiers.pop(index)

            if neighbour.visited or neighbour.blocked:
                continue

            self.remove_wall(current, neighbour)
            neighbour.visited = True
            visited_count += 1
            self._notify_progress(
                progress_callback, visited_count, total_cells, "prim")

            for next_neighbour in self.get_unvisited_neighbours(neighbour):
                frontiers.append((neighbour, next_neighbour))

    def generate(
        self,
        algorithm: str,
        start_position: tuple[int, int] = (0, 0),
        progress_callback: ProgressCallback | None = None,
    ) -> None:
        """Generate a maze using the selected algorithm."""
        if algorithm == "dfs":
            self.generate_dfs(start_position, progress_callback)
        elif algorithm == "prim":
            self.generate_prim(start_position, progress_callback)
        else:
            raise ValueError(f"Unsupported algo: {algorithm}")

    def add_extra_openings(self, count: int) -> None:
        """Open extra walls to create loops for non-perfect mazes."""
        candidates = self._closed_internal_edges()
        self.random.shuffle(candidates)
        opened = 0

        for current, neighbour in candidates:
            self.remove_wall(current, neighbour)
            if self.has_large_open_area():
                self.close_wall(current, neighbour)
                continue

            opened += 1
            if opened >= count:
                return

    def _closed_internal_edges(self) -> list[tuple[Cell, Cell]]:
        """Return closed edges between adjacent non-blocked cells."""
        edges: list[tuple[Cell, Cell]] = []

        for y in range(self.height):
            for x in range(self.width):
                cell = self.get_cell(x, y)
                if cell.blocked:
                    continue

                if x < self.width - 1:
                    neighbour = self.get_cell(x + 1, y)
                    if not neighbour.blocked and cell.east:
                        edges.append((cell, neighbour))

                if y < self.height - 1:
                    neighbour = self.get_cell(x, y + 1)
                    if not neighbour.blocked and cell.south:
                        edges.append((cell, neighbour))

        return edges

    def close_wall(self, current: Cell, neighbour: Cell) -> None:
        """Close the wall between two adjacent cells."""
        dx = neighbour.x - current.x
        dy = neighbour.y - current.y

        if dx == 1 and dy == 0:
            current.east = True
            neighbour.west = True
        elif dx == -1 and dy == 0:
            current.west = True
            neighbour.east = True
        elif dx == 0 and dy == 1:
            current.south = True
            neighbour.north = True
        elif dx == 0 and dy == -1:
            current.north = True
            neighbour.south = True
        else:
            raise ValueError("Cells : are not adjacent")

    def validate_maze(self) -> bool:
        """Check wall consistency between neighbour cells."""
        for y in range(self.height):
            for x in range(self.width):
                cell = self.get_cell(x, y)

                if x < self.width - 1:
                    east_neighbour = self.get_cell(x + 1, y)

                    if cell.east != east_neighbour.west:
                        return False

                if y < self.height - 1:
                    south_neighbour = self.get_cell(x, y + 1)

                    if cell.south != south_neighbour.north:
                        return False

        return True

    def validate_connectivity(
        self,
        entry: tuple[int, int],
    ) -> bool:
        """Check that every non-blocked cell is reachable from entry."""
        start = self.get_cell(entry[0], entry[1])
        if start.blocked:
            return False

        stack: list[Cell] = [start]
        visited: set[tuple[int, int]] = {(start.x, start.y)}

        while stack:
            cell = stack.pop()
            x = cell.x
            y = cell.y

            if not cell.north and y > 0:
                neighbour = self.get_cell(x, y - 1)
                if not neighbour.blocked and (x, y - 1) not in visited:
                    visited.add((x, y - 1))
                    stack.append(neighbour)
            if not cell.east and x < self.width - 1:
                neighbour = self.get_cell(x + 1, y)
                if not neighbour.blocked and (x + 1, y) not in visited:
                    visited.add((x + 1, y))
                    stack.append(neighbour)
            if not cell.south and y < self.height - 1:
                neighbour = self.get_cell(x, y + 1)
                if not neighbour.blocked and (x, y + 1) not in visited:
                    visited.add((x, y + 1))
                    stack.append(neighbour)
            if not cell.west and x > 0:
                neighbour = self.get_cell(x - 1, y)
                if not neighbour.blocked and (x - 1, y) not in visited:
                    visited.add((x - 1, y))
                    stack.append(neighbour)

        return len(visited) == self.count_open_cells()

    def has_large_open_area(self) -> bool:
        """Return True if a fully open 3x3 area exists."""
        for y in range(self.height - 2):
            for x in range(self.width - 2):
                if self._is_open_3_by_3(x, y):
                    return True
        return False

    def _is_open_3_by_3(self, start_x: int, start_y: int) -> bool:
        """Check whether a 3x3 block has no internal walls."""
        for y in range(start_y, start_y + 3):
            for x in range(start_x, start_x + 3):
                if self.get_cell(x, y).blocked:
                    return False

        for y in range(start_y, start_y + 3):
            for x in range(start_x, start_x + 2):
                if self.get_cell(x, y).east:
                    return False

        for y in range(start_y, start_y + 2):
            for x in range(start_x, start_x + 3):
                if self.get_cell(x, y).south:
                    return False

        return True

    def block_cells(self, positions: set[tuple[int, int]]) -> None:
        """Mark given cells as blocked and fully closed."""
        for x, y in positions:
            cell = self.get_cell(x, y)
            cell.blocked = True
            cell.north = True
            cell.east = True
            cell.south = True
            cell.west = True
            cell.visited = True

    def add_test_block(self) -> None:
        """Add a small blocked pattern for testing."""
        self.block_cells({
            (1, 1),
            (2, 1),
            (1, 2),
        })

    def add_42_pattern(self) -> None:
        """Add the 42 pattern in the maze"""
        pattern_height = len(PATTERN_42)
        pattern_width = len(PATTERN_42[0])

        if self.width < pattern_width + 2 or self.height < pattern_height + 2:
            print("Maze too small to display the 42 pattern.", file=sys.stderr)
            return

        start_x = (self.width - pattern_width) // 2
        start_y = (self.height - pattern_height) // 2

        positions_a_bloquer: set[tuple[int, int]] = set()

        for dy, ligne in enumerate(PATTERN_42):
            for dx, caractere in enumerate(ligne):
                if caractere == "#":
                    abs_x = start_x + dx
                    abs_y = start_y + dy
                    positions_a_bloquer.add((abs_x, abs_y))

        self.block_cells(positions_a_bloquer)
