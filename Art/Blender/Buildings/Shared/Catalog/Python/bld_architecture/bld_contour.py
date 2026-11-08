# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass
from enum import Enum

from .bld_side import Side

Point = tuple[int, int]


class CornerKind(Enum):
    """Kind of a contour corner, seen from the building."""

    OUTER = "outer"
    INNER = "inner"


@dataclass(frozen=True)
class ContourCorner:
    """One corner of a contour ring."""

    point: Point
    """Grid point in m, one cell is 1 m."""
    kind: CornerKind
    """Outer (convex) or inner (concave)."""


@dataclass(frozen=True)
class ContourSegment:
    """Straight stretch of wall between two corners."""

    start: Point
    """Grid point where the segment begins."""
    end: Point
    """Grid point where the segment ends."""
    outward: Side
    """Side the outside of the building lies on."""

    @property
    def length(self) -> int:
        """Length of the segment in m."""
        return abs(self.end[0] - self.start[0]) + abs(self.end[1] - self.start[1])


@dataclass(frozen=True)
class ContourRing:
    """Closed contour, segment i runs from corner i to corner i + 1 (wrapping)."""

    corners: tuple[ContourCorner, ...]
    """Corners in walking order, interior on the left."""
    segments: tuple[ContourSegment, ...]
    """Segments in walking order."""

    def __post_init__(self) -> None:
        """Validates that corners and segments belong together.

        Raises:
            ValueError: If the counts differ or the turn balance is not +-4.

        Returns:
            None.
        """
        if len(self.corners) != len(self.segments):
            raise ValueError("A ring needs exactly one segment per corner")
        outer_count: int = sum(1 for corner in self.corners if corner.kind is CornerKind.OUTER)
        inner_count: int = len(self.corners) - outer_count
        if abs(outer_count - inner_count) != 4:
            raise ValueError(
                f"Ring is not closed: {outer_count} outer, {inner_count} inner corners"
            )
        return None

    @property
    def is_hole(self) -> bool:
        """Whether the ring encloses an empty area (more inner than outer corners)."""
        outer_count: int = sum(1 for corner in self.corners if corner.kind is CornerKind.OUTER)
        return outer_count < len(self.corners) - outer_count
