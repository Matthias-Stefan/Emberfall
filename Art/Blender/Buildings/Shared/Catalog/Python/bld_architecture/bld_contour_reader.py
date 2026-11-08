# Copyright (c) 2026 Emberfall. All Rights Reserved.
# bld_architecture/bld_contour_reader.py

from collections import defaultdict

from .bld_contour import ContourCorner, ContourRing, ContourSegment, CornerKind, Point
from .bld_footprint import Footprint
from .bld_side import Side

# east, north, west, south: counter-clockwise, so +1 is a left turn
_DIRECTIONS: tuple[Point, ...] = ((1, 0), (0, 1), (-1, 0), (0, -1))
# walking with the interior on the left, the outside is on the right
_OUTWARD: tuple[Side, ...] = (Side.SOUTH, Side.EAST, Side.NORTH, Side.WEST)


class ContourReader:
    """Reads the closed outer contours of a footprint."""

    def read(self, footprint: Footprint) -> tuple[ContourRing, ...]:
        """Extracts all contour rings.

        Args:
            footprint: Footprint to read.

        Returns:
            One ring per closed contour, holes (courtyards) included.
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

        rings: list[ContourRing] = []
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
        raise ValueError(f"Contour dead end at {current}")

    def _build_ring(self, points: list[Point]) -> ContourRing:
        """Reduces a point walk to corners and straight segments.

        Args:
            points: Every grid point of one ring in walking order.

        Returns:
            The ring, starting at its first corner.
        """
        count: int = len(points)
        corner_indices: list[int] = []
        corners: list[ContourCorner] = []

        for index, point in enumerate(points):
            incoming: int = self._direction_of(points[index - 1], point)
            leaving: int = self._direction_of(point, points[(index + 1) % count])
            turn: int = (leaving - incoming) % 4
            if turn == 0:
                continue
            if turn == 2:
                raise ValueError(f"U-turn in contour at {point}")
            corner_indices.append(index)
            corners.append(
                ContourCorner(point, CornerKind.OUTER if turn == 1 else CornerKind.INNER)
            )

        segments: list[ContourSegment] = []
        for corner_number, start_index in enumerate(corner_indices):
            end_index: int = corner_indices[(corner_number + 1) % len(corner_indices)]
            direction: int = self._direction_of(
                points[start_index], points[(start_index + 1) % count]
            )
            segments.append(
                ContourSegment(points[start_index], points[end_index], _OUTWARD[direction])
            )
        return ContourRing(tuple(corners), tuple(segments))
