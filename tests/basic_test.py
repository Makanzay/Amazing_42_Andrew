from mazegen.generator import MazeGenerator
from mazegen.renderer import render_ascii
from mazegen.solver import solve_shortest_path


def test_dfs_generates_connected_maze() -> None:
    generator = MazeGenerator(8, 6, seed=42)
    generator.generate("dfs", start_position=(0, 0))

    assert generator.validate_maze()
    assert generator.validate_connectivity((0, 0))
    assert not generator.has_large_open_area()


def test_prim_generates_connected_maze() -> None:
    generator = MazeGenerator(8, 6, seed=42)
    generator.generate("prim", start_position=(0, 0))

    assert generator.validate_maze()
    assert generator.validate_connectivity((0, 0))
    assert not generator.has_large_open_area()


def test_solver_returns_path() -> None:
    generator = MazeGenerator(5, 5, seed=7)
    generator.generate("dfs", start_position=(0, 0))

    path = solve_shortest_path(generator.grid, (0, 0), (4, 4))

    assert path
    assert set(path) <= {"N", "E", "S", "W"}


def test_ascii_render_contains_markers() -> None:
    generator = MazeGenerator(5, 5, seed=7)
    generator.generate("prim", start_position=(0, 0))
    path = solve_shortest_path(generator.grid, (0, 0), (4, 4))

    output = render_ascii(
        generator.grid,
        (0, 0),
        (4, 4),
        path,
        use_color=False,
    )

    assert " S " in output
    assert " E " in output
    assert " . " in output
