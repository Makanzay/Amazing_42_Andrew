#! /usr/bin/env python3
import sys
from dataclasses import dataclass

from mazegen.cell import Cell
from mazegen.config import MazeConfig, parse_config_file
from mazegen.generator import MazeGenerator
from mazegen.renderer import render_ascii
from mazegen.solver import solve_shortest_path
from mazegen.writer import write_maze_file

COLOR_CHOICES = [
    "white",
    "red",
    "green",
    "blue",
    "yellow",
    "cyan",
    "magenta",
    "gray",
]


@dataclass
class MazeRun:
    """Generated maze data needed by writers and renderers."""

    generator: MazeGenerator
    path: str


def clear_terminal() -> None:
    """Clear the terminal screen."""
    sys.stdout.write("\033[2J\033[3J\033[H")
    sys.stdout.flush()


def build_maze(config: MazeConfig, seed_offset: int = 0) -> MazeRun:
    """Generate, validate, solve, and write one maze."""
    clear_terminal()

    seed = config.seed
    if seed is not None:
        seed += seed_offset

    generator = MazeGenerator(
        width=config.width,
        height=config.height,
        seed=seed,
    )
    generator.add_42_pattern()

    generator.generate(
        config.algorithm,
        start_position=config.entry,
    )
    if not config.perfect:
        loop_count = max(1, generator.count_open_cells() // 20)
        generator.add_extra_openings(loop_count)

    if not generator.validate_maze():
        raise ValueError("Generated maze has inconsistent walls")
    if not generator.validate_connectivity(config.entry):
        raise ValueError("Generated maze is not fully connected")
    if generator.has_large_open_area():
        raise ValueError("Generated maze contains a 3x3 open area")

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

    return MazeRun(generator=generator, path=path)


def next_color(color: str) -> str:
    """Return the next supported display colour."""
    index = COLOR_CHOICES.index(color)
    return COLOR_CHOICES[(index + 1) % len(COLOR_CHOICES)]


def print_ascii_maze(
    maze_run: MazeRun,
    config: MazeConfig,
    show_path: bool,
    wall_color: str,
) -> None:
    """Print the current maze in ASCII mode."""
    visible_path = maze_run.path if show_path else ""

    clear_terminal()
    print(render_ascii(
        maze_run.generator.grid,
        config.entry,
        config.exit,
        visible_path,
        wall_color=wall_color,
        path_color=config.path_color,
        pattern_color=config.pattern_color,
    ))
    print()
    print("Commands: [P] path  [R] regenerate  [C] wall color  [Q] quit")


def run_ascii(config: MazeConfig, maze_run: MazeRun) -> None:
    """Run the interactive ASCII display."""
    show_path = config.show_path
    wall_color = config.wall_color
    regeneration_count = 0

    while True:
        print_ascii_maze(maze_run, config, show_path, wall_color)
        try:
            command = input("> ").strip().lower()
        except EOFError:
            print("User run an CTRl + D ")
            return

        if command == "q":
            return
        if command == "p":
            show_path = not show_path
        elif command == "r":
            regeneration_count += 1
            maze_run = build_maze(config, regeneration_count)
        elif command == "c":
            wall_color = next_color(wall_color)
        elif command:
            print("Unknown command. Use P, R, C or Q.")


def main() -> None:
    """Main Generator => parseconfi"""
    if len(sys.argv) != 2:
        raise ValueError("Usage: python3 a_maze_ing.py config.txt")

    config: MazeConfig = parse_config_file(sys.argv[1])

    maze_run = build_maze(config)
    if config.display == "mlx":
        from mazegen.mlx_renderer import MlxRenderer

        regeneration_count = 0

        def regenerate() -> tuple[list[list[Cell]], str]:
            nonlocal regeneration_count
            regeneration_count += 1
            new_run = build_maze(config, regeneration_count)
            return new_run.generator.grid, new_run.path

        renderer = MlxRenderer(
            maze_run.generator.grid,
            config.entry,
            config.exit,
            path=maze_run.path,
            show_path=config.show_path,
            wall_color=config.wall_color,
            path_color=config.path_color,
            pattern_color=config.pattern_color,
            regenerate_callback=regenerate,
        )
        renderer.run()
    else:
        run_ascii(config, maze_run)


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.", file=sys.stderr)
        sys.exit(130)

    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
