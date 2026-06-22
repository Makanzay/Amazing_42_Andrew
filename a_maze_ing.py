#! /usr/bin/python3
try:
    import sys

    from mazegen.generator import MazeGenerator
    from mazegen.writer import write_maze_file
    from mazegen.solver import solve_shortest_path

except (ImportError, KeyboardInterrupt, Exception) as e:
    print(f"Import Error : {e}")


def main() -> None:
    generator = MazeGenerator(4, 4, seed=42)
    generator.generate_dfs()

    path = solve_shortest_path(
        generator.grid,
        entry=(0, 0),
        exit_=(3, 3),
    )

    write_maze_file(
        grid=generator.grid,
        output_file="maze.txt",
        entry=(0, 0),
        exit_=(3, 3),
        path=path,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error : {e}", file=sys.stderr)
        sys.exit(1)
