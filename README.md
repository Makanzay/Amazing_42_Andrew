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

### Local Type Stubs

The `typings/` directory contains a local mypy stub for the MiniLibX `mlx`
package. The wheel used by this project works at runtime, but it does not ship
Python type information. The stub in `typings/mlx/__init__.pyi` describes only
the `Mlx` methods used by this codebase, so `make lint` and `make lint-strict`
can type-check the project without ignoring the `mlx` import.

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
SHOW_PATH=True
WALL_COLOR=white
PATH_COLOR=yellow
PATTERN_COLOR=blue
```

Supported algorithms are `dfs` and `prim`. Supported display modes are `ascii`
and `mlx`. Supported colours are `white`, `red`, `green`, `blue`, `yellow`,
`cyan`, `magenta`, and `gray`.

## Algorithms

This project uses two algorithms to build mazes, and one algorithm to solve
them.

### DFS Generation

DFS means depth-first search. Imagine a child walking in a maze with a pencil:
they keep walking forward as long as they find a new place. When they get stuck,
they go back to the last place where another direction was possible, then try
again.

In this project, DFS starts from the entry cell, chooses a random unvisited
neighbour, opens the wall between both cells, and continues until every available
cell has been visited. The implementation is iterative, so it uses a Python list
as a stack instead of recursive function calls.

```python
from mazegen import MazeGenerator

generator = MazeGenerator(width=20, height=15, seed=42)
generator.add_42_pattern()
generator.generate("dfs", start_position=(0, 0))

grid = generator.grid
```

DFS is the default because it is simple, reproducible with a seed, and naturally
creates a perfect maze over all non-blocked cells.

### Prim Generation

Prim starts from one cell too, but it thinks more like this: "I have a growing
island of visited cells. Around my island, there are frontier walls. I randomly
choose one frontier wall, open it, and add the new cell to my island."

In this project, randomized Prim keeps a list of frontier edges. Each edge links
an already visited cell to an unvisited neighbour. The algorithm picks one edge
at random, opens that wall, marks the neighbour as visited, then adds that
neighbour's new frontier edges.

```python
from mazegen import MazeGenerator

generator = MazeGenerator(width=20, height=15, seed=42)
generator.add_42_pattern()
generator.generate("prim", start_position=(0, 0))

grid = generator.grid
```

Prim also creates a perfect maze when `PERFECT=True`, but the result has a
different style: branches are usually more evenly spread than with DFS.

### BFS Solving

BFS means breadth-first search. It is used here to find the shortest path from
the entry to the exit. Imagine dropping water at the entrance: the water spreads
one step at a time in every possible direction. The first time it reaches the
exit, that route is the shortest one.

In this project, BFS stores cells in a queue. Each item keeps both the current
cell and the path used to reach it. When the exit is found, the solver returns a
string made of `N`, `E`, `S`, and `W`.

```python
from mazegen import MazeGenerator, solve_shortest_path

generator = MazeGenerator(width=20, height=15, seed=42)
generator.add_42_pattern()
generator.generate("dfs", start_position=(0, 0))

path = solve_shortest_path(
    generator.grid,
    entry=(0, 0),
    exit_=(19, 14),
)

print(path)
```

The returned path is also written to the output file after the maze data, entry,
and exit coordinates.

When `PERFECT=False`, the program first generates a connected maze, then opens a
small number of additional internal walls to create loops. Each extra opening is
checked so the maze still avoids fully open 3x3 areas.

The visible `42` pattern is made from fully closed blocked cells. If the maze is
too small for the pattern, the program prints a clear message and continues
without it.

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
Before each generation or regeneration, the program sends ANSI clear-screen
codes (`\033[2J\033[3J\033[H`) so old mazes are removed from the visible
terminal and from the scrollback when the terminal supports it. If the program
is launched from an IDE output panel that does not interpret ANSI escape codes,
old mazes may still appear; use a real terminal or the VS Code integrated
terminal in that case.

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
- ASCII spinning donut inspiration: https://www.asciiart.eu/animations/ascii-spinning-donut
- 42 MiniLibX documentation supplied with the local `mlx` wheel
