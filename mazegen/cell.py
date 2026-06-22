""" every maze cases as an object with data needed"""

from dataclasses import dataclass


@dataclass
class Cell:
    """representation of the cell of our maze
    each wall and their position
    -----------------------------------------
    True -> closed wall
    False -> open wall
    (x,y) -> mathematical represention of the position
    """
    x: int
    y: int

    north: bool = True
    east: bool = True
    south: bool = True
    west: bool = True

    visited: bool = False

    def to_hexa(self) -> str:
        """converter to Hexadecimal
        uses a 4bit data to represent wall state
        through bitwise and return an Hexadecimal
        output
        """
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
