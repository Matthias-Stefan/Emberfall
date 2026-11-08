# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass


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
