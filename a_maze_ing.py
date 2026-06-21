#! usr/bin/python3

from mazegen.cell import Cell


def main() -> None:
    cell = Cell(0, 0)
    print(cell)
    print(cell.to_hexa())


if __name__ == "__main__":
    main()
