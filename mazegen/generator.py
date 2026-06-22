from .cell import Cell
import random


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

    def generate_dfs(self) -> None:
        """Generate a perfect maze using iterative dfs backtracking
        allow use to avoid recursive error on wide maze"""
        start = self.get_cell(0, 0)

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
    
    def validate_maze
