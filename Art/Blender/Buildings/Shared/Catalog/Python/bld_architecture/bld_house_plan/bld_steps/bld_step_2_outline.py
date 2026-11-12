# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 2: footprint -> outline rings, the closed edges of the footprint as corners and straight segments."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

from .bld_step_1_footprint import Footprint, Side

Point = tuple[int, int]


class CornerKind(Enum):
    """Kind of an outline corner, seen from the building."""

    OUTER = "outer"
    INNER = "inner"


@dataclass(frozen=True)
class OutlineCorner:
    """One corner of an outline ring."""

    point: Point
    """Grid point in m, one cell is 1 m."""
    kind: CornerKind
    """Outer (convex) or inner (concave)."""


@dataclass(frozen=True)
class OutlineSegment:
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
class OutlineRing:
    """Closed outline, segment i runs from corner i to corner i + 1 (wrapping)."""

    corners: tuple[OutlineCorner, ...]
    """Corners in walking order, interior on the left."""
    segments: tuple[OutlineSegment, ...]
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


# east, north, west, south: counter-clockwise, so +1 is a left turn
_DIRECTIONS: tuple[Point, ...] = ((1, 0), (0, 1), (-1, 0), (0, -1))
# walking with the interior on the left, the outside is on the right
_OUTWARD: tuple[Side, ...] = (Side.SOUTH, Side.EAST, Side.NORTH, Side.WEST)


class OutlineReader:
    """Reads the closed outer outlines of a footprint."""

    def read(self, footprint: Footprint) -> tuple[OutlineRing, ...]:
        """Extracts all outline rings.

        Args:
            footprint: Footprint to read.

        Returns:
            One ring per closed outline, holes (courtyards) included.
        """
        cells: frozenset[Point] = footprint.main_cells.union(*footprint.extension_cells)
        outgoing: dict[Point, list[Point]] = defaultdict(list)

        # every edge runs with the building on its left
        for cell_x, cell_y in sorted(cells):
            if (cell_x, cell_y - 1) not in cells:
                outgoing[(cell_x, cell_y)].append((cell_x + 1, cell_y))
            if (cell_x + 1, cell_y) not in cells:
                outgoing[(cell_x + 1, cell_y)].append((cell_x + 1, cell_y + 1))
            if (cell_x, cell_y + 1) not in cells:
                outgoing[(cell_x + 1, cell_y + 1)].append((cell_x, cell_y + 1))
            if (cell_x - 1, cell_y) not in cells:
                outgoing[(cell_x, cell_y + 1)].append((cell_x, cell_y))

        rings: list[OutlineRing] = []
        while outgoing:
            start: Point = min(outgoing)
            rings.append(self._build_ring(self._walk(start, outgoing)))
        return tuple(rings)

    @staticmethod
    def _direction_of(start: Point, end: Point) -> int:
        """Returns the index into _DIRECTIONS for a unit step."""
        return _DIRECTIONS.index((end[0] - start[0], end[1] - start[1]))

    def _walk(self, start: Point, outgoing: dict[Point, list[Point]]) -> list[Point]:
        """Follows unit edges until the ring closes, consuming them.

        Args:
            start: Point to begin at.
            outgoing: Unused edges per start point, edited in place.

        Returns:
            Every grid point of the ring in walking order, collinear ones included.
        """
        points: list[Point] = [start]
        current: Point = start
        previous_direction: int | None = None

        while True:
            candidates: list[Point] = outgoing[current]
            next_point: Point = self._pick_next(current, candidates, previous_direction)
            candidates.remove(next_point)
            if not candidates:
                del outgoing[current]

            previous_direction = self._direction_of(current, next_point)
            current = next_point
            if current == start:
                return points
            points.append(current)

    def _pick_next(
        self, current: Point, candidates: list[Point], previous_direction: int | None
    ) -> Point:
        """Chooses the next edge, preferring the leftmost turn.

        Taking the leftmost turn keeps two cells that only touch diagonally
        in separate rings.
        """
        if previous_direction is None:
            return min(candidates)
        for turn in (1, 0, 3):  # left, straight, right
            wanted: int = (previous_direction + turn) % 4
            for candidate in candidates:
                if self._direction_of(current, candidate) == wanted:
                    return candidate
        raise ValueError(f"Outline dead end at {current}")

    def _build_ring(self, points: list[Point]) -> OutlineRing:
        """Reduces a point walk to corners and straight segments.

        Args:
            points: Every grid point of one ring in walking order.

        Returns:
            The ring, starting at its first corner.
        """
        count: int = len(points)
        corner_indices: list[int] = []
        corners: list[OutlineCorner] = []

        for index, point in enumerate(points):
            incoming: int = self._direction_of(points[index - 1], point)
            leaving: int = self._direction_of(point, points[(index + 1) % count])
            turn: int = (leaving - incoming) % 4
            if turn == 0:
                continue
            if turn == 2:
                raise ValueError(f"U-turn in outline at {point}")
            corner_indices.append(index)
            corners.append(
                OutlineCorner(point, CornerKind.OUTER if turn == 1 else CornerKind.INNER)
            )

        segments: list[OutlineSegment] = []
        for corner_number, start_index in enumerate(corner_indices):
            end_index: int = corner_indices[(corner_number + 1) % len(corner_indices)]
            direction: int = self._direction_of(
                points[start_index], points[(start_index + 1) % count]
            )
            segments.append(
                OutlineSegment(points[start_index], points[end_index], _OUTWARD[direction])
            )
        return OutlineRing(tuple(corners), tuple(segments))
