#! /usr/bin/env python3
try:
    import sys

    from mazegen.generator import MazeGenerator
    from mazegen.writer import write_maze_file
    from mazegen.solver import solve_shortest_path
    from mazegen.config import parse_config_file, MazeConfig
    from mazegen.renderer import render_ascii

except (ImportError, KeyboardInterrupt, Exception) as e:
    print(f"Import Error : {e}")


def check_arg(argument: list[str]) -> bool:
    """param checker to assure the correct parsing"""
    run_file: bool = (str(argument[0]) == "a_maze_ing.py")
    config_file: bool = (str(argument[1]) == "config.txt")

    return run_file and config_file


def main() -> None:
    """Main Generator => parseconfi"""
    if len(sys.argv) != 2:
        raise ValueError("Usage: python3 a_maze_ing.py config.txt")
    if not check_arg(sys.argv):
        raise ValueError("Use the correct ... a_maze_ing.py config.txt")

    config: MazeConfig = parse_config_file(sys.argv[1])

    generator = MazeGenerator(
        width=config.width,
        height=config.height,
        seed=config.seed)
    generator.add_42_pattern()
    
    if config.algorithm == "dfs":
        generator.generate_dfs()
        if not generator.validate_maze():
            raise ValueError("Generated maze has inconsistent walls")
    else:
        raise ValueError(f"Unsupported algo: {config.algorithm}")

    path = solve_shortest_path(
        generator.grid,
        entry=config.entry,
        exit_=config.exit,
    )

    write_maze_file(
        grid=generator.grid,
        output_file=config.output_file,
        entry=config.entry,
        exit_=config.exit,
        path=path,
    )

    print(render_ascii(generator.grid, config.entry, config.exit, path))


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
        sys.exit(130)

    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
