#! usr/bin/python3

from mazegen.cell import Cell
from mazegen.generator import MazeGenerator
from mazegen.writer import write_maze_file


__all__ = [Cell, MazeGenerator, write_maze_file]


def main() -> None:
    """first test"""
    gen_maze: MazeGenerator = MazeGenerator(5, 4, seed=42)
    gen_maze.generate_dfs()
    write_maze_file(
        grid=gen_maze.grid,
        output_file="maze.txt",
        entry=(0, 0),
        exit_=(3, 3),
        path="Temporaire"
    )


if __name__ == "__main__":
    main()
