""" every maze cases as an object with data needed"""

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

    def to_hexa(self) -> str:
        """converter to Hexadecimal"""
        res = 0

        if self.north:
            res |= 1
        if self.east:
            res |= 2
        if self.south:
            res |= 4
        if self.west:
            res |= 8

        return f"{res:X}"
