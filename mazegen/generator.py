import random
import sys

from .cell import Cell

PATTERN_42 = [
    "#   #  ### ",
    "#   # #   #",
    "#####    # ",
    "    #   #  ",
    "    # #####",
]

Direction = tuple[str, int, int, str]
DIRECTIONS: tuple[Direction, ...] = (
    ("north", 0, -1, "south"),
    ("east", 1, 0, "west"),
    ("south", 0, 1, "north"),
    ("west", -1, 0, "east"),
)


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
                self.close_cell(cell)
                cell.visited = cell.blocked

    def close_cell(self, cell: Cell) -> None:
        """Close every wall of one cell."""
        cell.north = True
        cell.east = True
        cell.south = True
        cell.west = True

    def count_open_cells(self) -> int:
        """Return the number of non-blocked cells in the maze."""
        return sum(
            1
            for row in self.grid
            for cell in row
            if not cell.blocked
        )

    def remove_wall(self, current: Cell, neighbour: Cell) -> None:
        """Remove the wall between two adjacent cells."""
        self._set_wall(current, neighbour, closed=False)

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
        neighbours: list[Cell] = []

        for _, dx, dy, _ in DIRECTIONS:
            x = cell.x + dx
            y = cell.y + dy
            if self.is_inside(x, y):
                neighbours.append(self.get_cell(x, y))

        return neighbours

    def is_inside(self, x: int, y: int) -> bool:
        """Return True when coordinates are inside the maze."""
        return 0 <= x < self.width and 0 <= y < self.height

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
    ) -> None:
        """Generate a perfect maze using iterative dfs backtracking
        allow use to avoid recursive error on wide maze"""
        self.reset_walls()
        start = self.get_cell(start_position[0], start_position[1])

        if start.blocked:
            raise ValueError("Cant Start here cell is blocked")
        start.visited = True

        stack: list[Cell] = [start]

        while stack:
            current = stack[-1]
            unvisited = self.get_unvisited_neighbours(current)

            if unvisited:
                neighbour = self.random.choice(unvisited)
                self.remove_wall(current, neighbour)
                neighbour.visited = True
                stack.append(neighbour)
            else:
                stack.pop()

    def generate_prim(
        self,
        start_position: tuple[int, int] = (0, 0),
    ) -> None:
        """Generate a perfect maze using randomized Prim's algorithm."""
        self.reset_walls()
        start = self.get_cell(start_position[0], start_position[1])

        if start.blocked:
            raise ValueError("Cant Start here cell is blocked")

        start.visited = True
        frontiers: list[tuple[Cell, Cell]] = []

        for neighbour in self.get_unvisited_neighbours(start):
            frontiers.append((start, neighbour))

        while frontiers:
            index = self.random.randrange(len(frontiers))
            current, neighbour = frontiers.pop(index)

            if neighbour.visited or neighbour.blocked:
                continue

            self.remove_wall(current, neighbour)
            neighbour.visited = True

            for next_neighbour in self.get_unvisited_neighbours(neighbour):
                frontiers.append((neighbour, next_neighbour))

    def generate(
        self,
        algorithm: str,
        start_position: tuple[int, int] = (0, 0),
    ) -> None:
        """Generate a maze using the selected algorithm."""
        if algorithm == "dfs":
            self.generate_dfs(start_position)
        elif algorithm == "prim":
            self.generate_prim(start_position)
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
        self._set_wall(current, neighbour, closed=True)

    def _set_wall(self, current: Cell, neighbour: Cell, closed: bool) -> None:
        """Set the shared wall between two adjacent cells."""
        dx = neighbour.x - current.x
        dy = neighbour.y - current.y

        for current_wall, wall_dx, wall_dy, neighbour_wall in DIRECTIONS:
            if dx == wall_dx and dy == wall_dy:
                setattr(current, current_wall, closed)
                setattr(neighbour, neighbour_wall, closed)
                return

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

            for wall, dx, dy, _ in DIRECTIONS:
                next_x = x + dx
                next_y = y + dy
                position = (next_x, next_y)

                if getattr(cell, wall) or not self.is_inside(next_x, next_y):
                    continue
                if position in visited:
                    continue

                neighbour = self.get_cell(next_x, next_y)
                if neighbour.blocked:
                    continue

                visited.add(position)
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
            self.close_cell(cell)
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
