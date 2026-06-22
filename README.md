*This project has been created as part of the 42 curriculum by lmpolo.*

# A-Maze-ing

## Description

A-Maze-ing is a Python 3.10 maze generator. It reads a plain text
configuration file, generates a valid maze, writes the hexadecimal wall
representation to an output file, solves the shortest path from entry to exit,
and displays the result either in the terminal or with MiniLibX.

The reusable generation code lives in the `mazegen` package. It can be imported
from another project, installed locally, and rebuilt as a wheel named `mazegen`.

## Instructions

Install dependencies and the local MiniLibX wheel:

```bash
make install
```

### MiniLibX Setup On Ubuntu / 42 School Machines

If the graphical display does not start, install the system libraries used by
the school MiniLibX wheel:

```bash
sudo apt update
sudo apt install -y libvulkan1 libxcb1 libxcb-keysyms1 libbsd0
```

Then activate the virtual environment and install the local wheel:

```bash
source .venv/bin/activate
pip install mlx-2.2-py3-none-any.whl
```

Some school archives may provide the same wheel with an Ubuntu-specific name. If
that is the file you received, install it directly:

```bash
pip install mlx-2.2-py3-ubuntu-any.whl
```

If pip refuses the wheel name or if you need to force a clean reinstall:

```bash
pip install --upgrade pip
pip install mlx-2.2-py3-ubuntu-any.whl --force-reinstall --no-deps
```

If the Ubuntu wheel filename is still rejected, rename it to a generic Python
wheel name and reinstall:

```bash
mv mlx-2.2-py3-ubuntu-any.whl mlx-2.2-py3-none-any.whl
pip install mlx-2.2-py3-none-any.whl --force-reinstall --no-deps
```

You can verify that MiniLibX is installed with this small script:

```python
import sys
from mlx import Mlx


def main() -> None:
    """Initialise MiniLibX and open a test window."""
    try:
        mlx_loader = Mlx()

        mlx_ptr = mlx_loader.mlx_init()
        if not mlx_ptr:
            raise RuntimeError("mlx_init() failed")

        win_ptr = mlx_loader.mlx_new_window(
            mlx_ptr,
            400,
            400,
            "Mon Labyrinthe 42",
        )
        if not win_ptr:
            raise RuntimeError("mlx_new_window() failed")

        print("MiniLibX is configured successfully.")
        print("Close the window or press Ctrl+C in the terminal to quit.")

        mlx_loader.mlx_loop(mlx_ptr)

    except Exception as error:
        print(f"MiniLibX initialisation error: {error}", file=sys.stderr)


if __name__ == "__main__":
    main()
```

Save it as a temporary file, run it with `.venv/bin/python`, and check that a
400x400 window opens.

Run the project:

```bash
make run
```

Equivalent direct command:

```bash
.venv/bin/python a_maze_ing.py config.txt
```

Use `.venv/bin/python` or activate the virtual environment. A system `python3`
may import a different package named `mlx`.

Other useful commands:

```bash
make test
make lint
make clean
make build
```

## Configuration

The config file contains one `KEY=VALUE` pair per line. Empty lines and lines
starting with `#` are ignored.

Mandatory keys:

```text
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
```

Additional keys supported by this implementation:

```text
SEED=42
ALGORITHM=dfs
DISPLAY=mlx
ANIMATION=False
SHOW_PATH=True
PROGRESS=True
WALL_COLOR=white
PATH_COLOR=yellow
PATTERN_COLOR=blue
```

Supported algorithms are `dfs` and `prim`. Supported display modes are `ascii`
and `mlx`. Supported colours are `white`, `red`, `green`, `blue`, `yellow`,
`cyan`, `magenta`, and `gray`.

## Algorithms

The default algorithm is iterative depth-first search with backtracking. It is
simple, deterministic with a seed, avoids recursion depth issues, and naturally
creates a perfect maze over all non-blocked cells.

The bonus algorithm is randomized Prim. It also creates a spanning tree over the
available cells, but produces a different maze style with more evenly spread
branches.

The visible `42` pattern is made from fully closed blocked cells. If the maze is
too small for the pattern, the program prints a clear message and continues
without it.

When `PERFECT=False`, the program first generates a connected maze, then opens a
small number of additional internal walls to create loops. Each extra opening is
checked so the maze still avoids fully open 3x3 areas.

## Display

Both displays show walls, entry, exit, the `42` pattern, and the shortest path
when enabled. ASCII and MiniLibX share the same main interactions:

```text
P      show/hide shortest path
R      regenerate a new maze
C      cycle wall colour
Q      quit
```

MiniLibX also accepts:

```text
Esc    close the window
```

The terminal renderer supports ANSI colours, clears and redraws the maze after
each command, and can start with the path hidden by setting `SHOW_PATH=False`.

## Output File

The output file contains one hexadecimal digit per cell. Bits encode closed
walls:

```text
bit 0: north
bit 1: east
bit 2: south
bit 3: west
```

After an empty line, the file contains entry coordinates, exit coordinates, and
the shortest path using `N`, `E`, `S`, and `W`.

## Reusable Module

Basic usage:

```python
from mazegen import MazeGenerator, solve_shortest_path

generator = MazeGenerator(width=20, height=15, seed=42)
generator.add_42_pattern()
generator.generate("prim", start_position=(0, 0))

grid = generator.grid
path = solve_shortest_path(grid, (0, 0), (19, 14))
```

The reusable structure is `list[list[Cell]]`. Each `Cell` exposes coordinates,
wall booleans (`north`, `east`, `south`, `west`), and a `blocked` flag.

Build the package:

```bash
make build
```

The generated wheel appears in `dist/` and follows the required `mazegen-*`
package name pattern.

## Team And Project Management

This version was developed as a solo project. The work was split into parsing,
generation, solving, output format, display, then validation and documentation.
The plan evolved when MLX-specific rendering issues appeared: buffer alpha,
image synchronization, window close events, and `Ctrl+C` handling had to be
debugged separately from the maze logic.

What worked well: isolating generation from rendering made DFS, Prim, ASCII, and
MLX share the same data structure.

What could be improved: MiniLibX window-manager close events depend on the
Python wrapper, so keyboard-based closing remains more reliable than the window
cross on some school machines.

Tools used: Python virtual environment, pytest, flake8, mypy, MiniLibX, and AI
assistance for debugging, refactoring suggestions, documentation drafting, and
test planning. All generated changes were reviewed and tested locally.

## Resources

- Python documentation: https://docs.python.org/3/
- Pydantic documentation: https://docs.pydantic.dev/
- Maze generation overview: https://en.wikipedia.org/wiki/Maze_generation_algorithm
- Prim's algorithm: https://en.wikipedia.org/wiki/Prim%27s_algorithm
- 42 MiniLibX documentation supplied with the local `mlx` wheel
