from dataclasses import dataclass


@dataclass
class Cell:
    x: int
    y: int

    north: bool = True
    east: bool = True
    south: bool = True
    west: bool = True

    visited: bool = False
