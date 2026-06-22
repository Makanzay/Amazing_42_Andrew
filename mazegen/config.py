"""Parsing and data verification for the Config file"""
from pathlib import Path
import re

from pydantic import (BaseModel, Field, ValidationError,
                      field_validator, model_validator)
from .errors import ConfigError


CONFIG_LINE_RE = re.compile(r"^\s*([A-Z_]+)\s*=\s*(.+?)\s*$")


class MazeConfig(BaseModel):
    """Validation maze configuration param
    use of pydantic for data validation & conversion through
    our own BaseModel class
    --------------------------------------------
    class method here to build verification function
    that we want to run on our field verification by using the
    decorators field_validator and the cls class itself"""

    width: int = Field(alias="WIDTH", gt=0, le=500)
    height: int = Field(alias="HEIGHT", gt=0, le=500)
    entry: tuple[int, int] = Field(alias="ENTRY")
    exit: tuple[int, int] = Field(alias="EXIT")
    output_file: str = Field(alias="OUTPUT_FILE", min_length=1)
    perfect: bool = Field(alias="PERFECT")

    seed: int | None = Field(default=None, alias="SEED")
    algorithm: str = Field(default="dfs", alias="ALGORITHM")
    display: str = Field(default="mlx", alias="DISPLAY")
    animation: bool = Field(default=False, alias="ANIMATION")
    show_path: bool = Field(default=True, alias="SHOW_PATH")
    progress: bool = Field(default=True, alias="PROGRESS")
    wall_color: str = Field(default="white", alias="WALL_COLOR")
    path_color: str = Field(default="yellow", alias="PATH_COLOR")
    pattern_color: str = Field(default="blue", alias="PATTERN_COLOR")

    @field_validator("entry", "exit", mode="before")
    @classmethod
    def parse_coordinates(cls, value: str) -> tuple[int, int]:
        """Convert 'x,y' into a tuple of integers."""
        if not isinstance(value, str):
            raise ValueError("coordinates must be written as x,y")

        parts = value.split(",")
        if len(parts) != 2:
            raise ValueError("coordinates must contain exactly two values")

        return int(parts[0]), int(parts[1])

    @field_validator("algorithm")
    @classmethod
    def validate_algorithm(cls, value: str) -> str:
        """Validate selected maze algorithm."""
        value = value.lower()
        if value not in {"dfs", "prim"}:
            raise ValueError("algorithm must be dfs or prim")
        return value

    @field_validator("display")
    @classmethod
    def validate_display(cls, value: str) -> str:
        """Validate selected display mode."""
        value = value.lower()
        if value not in {"mlx", "ascii"}:
            raise ValueError("display must be mlx or ascii")
        return value

    @field_validator("wall_color", "path_color", "pattern_color")
    @classmethod
    def validate_color(cls, value: str) -> str:
        """Validate supported display colours."""
        value = value.lower()
        valid_colors = {
            "white",
            "red",
            "green",
            "blue",
            "yellow",
            "cyan",
            "magenta",
            "gray",
        }
        if value not in valid_colors:
            raise ValueError(
                "color must be one of: "
                + ", ".join(sorted(valid_colors))
            )
        return value

    @model_validator(mode="after")
    def validate_positions(self) -> "MazeConfig":
        """Validate entry and exit positions."""
        entry_x, entry_y = self.entry
        exit_x, exit_y = self.exit

        if self.entry == self.exit:
            raise ValueError("entry and exit must be different")

        if not (0 <= entry_x < self.width and 0 <= entry_y < self.height):
            raise ValueError("entry is outside maze bounds")

        if not (0 <= exit_x < self.width and 0 <= exit_y < self.height):
            raise ValueError("exit is outside maze bounds")

        return self


def parse_config_file(path: str) -> MazeConfig:
    """Read and validate a maze configuration file."""
    config_path = Path(path)

    if not config_path.exists():
        raise ConfigError(f"Config file not found: {path}")

    raw_config: dict[str, str] = {}

    try:
        with config_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                stripped = line.strip()

                if not stripped or stripped.startswith("#"):
                    continue

                match = CONFIG_LINE_RE.match(stripped)
                if match is None:
                    raise ConfigError(
                        f"Invalid syntax at line {line_number}: {stripped}"
                    )

                key, value = match.groups()
                if key in raw_config:
                    raise ConfigError(
                        f"Duplicate key '{key}'->line {line_number}")
                raw_config[key] = value

        return MazeConfig.model_validate(raw_config)

    except PermissionError as e:
        raise ConfigError(
            f"Permission denied for file: {path}") from e

    except IsADirectoryError as e:
        raise ConfigError(
            f"Expected a file but got a directory: {path}") from e

    except ValidationError as error:
        raise ConfigError(str(error)) from error
