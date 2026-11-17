# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Footprint of a building: its grid cells and the sides of cell rectangles."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass
from enum import Enum


class Side(Enum):
    """Side of a rectangle in cell space, Y points up."""

    NORTH = "north"
    EAST = "east"
    SOUTH = "south"
    WEST = "west"


@dataclass(frozen=True)
class CellRectangle:
    """Axis-aligned rectangle of grid cells, bounds inclusive."""

    min_x: int
    """Smallest X cell index."""
    min_y: int
    """Smallest Y cell index."""
    max_x: int
    """Largest X cell index."""
    max_y: int
    """Largest Y cell index."""

    def __post_init__(self) -> None:
        """Validates that the rectangle has at least one cell.

        Raises:
            ValueError: If a maximum lies below its minimum.

        Returns:
            None.
        """
        if self.max_x < self.min_x or self.max_y < self.min_y:
            raise ValueError(f"Empty rectangle: {self}")
        return None

    @property
    def width(self) -> int:
        """Extent along X in cells."""
        return self.max_x - self.min_x + 1

    @property
    def depth(self) -> int:
        """Extent along Y in cells."""
        return self.max_y - self.min_y + 1

    @property
    def area(self) -> int:
        """Number of cells."""
        return self.width * self.depth

    def cells(self) -> frozenset[tuple[int, int]]:
        """Returns all cells of the rectangle.

        Returns:
            Cell indices as (x, y) tuples.
        """
        return frozenset(
            (cell_x, cell_y)
            for cell_x in range(self.min_x, self.max_x + 1)
            for cell_y in range(self.min_y, self.max_y + 1)
        )


@dataclass(frozen=True)
class Footprint:
    """Built-up grid cells of one building."""

    seed: int
    """Seed the footprint was designed with, for reproducing it."""
    main_cells: frozenset[tuple[int, int]]
    """Cells of the main building as (x, y) indices."""
    extension_cells: tuple[frozenset[tuple[int, int]], ...] = ()
    """Cells per extension, in placement order."""

    @property
    def cells(self) -> frozenset[tuple[int, int]]:
        """All cells of the main building and its extensions."""
        return self.main_cells.union(*self.extension_cells)
