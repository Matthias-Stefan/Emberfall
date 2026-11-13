# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Builds the foundation band of a house, one closed mesh per outline ring."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import math

import bmesh

from bld_architecture import CornerCut, FoundationPlan, OutlineRing, Side

# outward unit normal per side, Y points up in cell space
_NORMALS: dict[Side, tuple[int, int]] = {
    Side.NORTH: (0, 1),
    Side.EAST: (1, 0),
    Side.SOUTH: (0, -1),
    Side.WEST: (-1, 0),
}


# outward unit normal per rotation of a module front: south, east, north, west
_NORMALS_BY_ROTATION: tuple[tuple[int, int], ...] = ((0, -1), (1, 0), (0, 1), (-1, 0))


def _unit(vector: tuple[float, float]) -> tuple[float, float]:
    """Scales a vector to length one.

    Args:
        vector is the vector.

    Returns:
        The vector with length one.
    """
    length: float = math.hypot(vector[0], vector[1])
    return vector[0] / length, vector[1] / length


class FoundationBuilder:
    """Builds a stone band along every outline ring, centered on the wall midline."""

    def __init__(self, foundation: FoundationPlan) -> None:
        """Creates a foundation builder.

        Args:
            foundation: Plan with the outline rings, height and overhang.

        Returns:
            None.
        """
        self._foundation: FoundationPlan = foundation
        return None

    @property
    def ring_count(self) -> int:
        """Number of rings, one mesh each."""
        return len(self._foundation.outlines)

    def build_ring(self, ring_index: int) -> bmesh.types.BMesh:
        """Builds the band of one ring as a closed solid.

        The band reaches from the inner wall face to the outer wall face plus the overhang, so it
        sticks out on the outside only and the floor slabs fill the inside.

        Args:
            ring_index: Index of the ring in the plan.

        Returns:
            A new BMesh in m, outline points are grid points, floor at Z = 0.
            The caller owns it and must call free() on it.
        """
        ring: OutlineRing = self._foundation.outlines[ring_index]
        wall_half: float = self._foundation.wall_depth * 0.5
        outer_reach: float = wall_half + self._foundation.overhang
        inner_reach: float = wall_half
        height: float = self._foundation.height

        bm: bmesh.types.BMesh = bmesh.new()
        outer_bottom: list[bmesh.types.BMVert] = []
        outer_top: list[bmesh.types.BMVert] = []
        inner_bottom: list[bmesh.types.BMVert] = []
        inner_top: list[bmesh.types.BMVert] = []

        # one point per corner with the unit normals of the walls before and after it, a cut corner
        # becomes two points with the diagonal between them
        corner_points: list[tuple[tuple[float, float], tuple[float, float], tuple[float, float]]] = []
        for corner_index, corner in enumerate(ring.corners):
            incoming: tuple[float, float] = _unit(_NORMALS[ring.segments[corner_index - 1].outward])
            leaving: tuple[float, float] = _unit(_NORMALS[ring.segments[corner_index].outward])
            point: tuple[float, float] = (float(corner.point[0]), float(corner.point[1]))
            cut: CornerCut | None = next(
                (candidate for candidate in self._foundation.cuts if candidate.point == point), None
            )
            if cut is None:
                corner_points.append((point, incoming, leaving))
                continue
            diagonal: tuple[float, float] = _unit(
                (_NORMALS_BY_ROTATION[cut.rotation][0] + _NORMALS_BY_ROTATION[(cut.rotation + 1) % 4][0],
                 _NORMALS_BY_ROTATION[cut.rotation][1] + _NORMALS_BY_ROTATION[(cut.rotation + 1) % 4][1])
            )
            back: tuple[int, int] = _NORMALS_BY_ROTATION[(cut.rotation + 1) % 4]
            along: tuple[int, int] = _NORMALS_BY_ROTATION[(cut.rotation + 2) % 4]
            corner_points.append(
                (
                    (point[0] - back[0] * cut.size, point[1] - back[1] * cut.size),
                    incoming,
                    diagonal,
                )
            )
            corner_points.append(
                (
                    (point[0] + along[0] * cut.size, point[1] + along[1] * cut.size),
                    diagonal,
                    leaving,
                )
            )

        count: int = len(corner_points)
        for point, incoming, leaving in corner_points:
            # the offset along the sum of both normals that keeps the band the same width on both walls
            scale: float = 1.0 / (1.0 + incoming[0] * leaving[0] + incoming[1] * leaving[1])
            direction_x: float = (incoming[0] + leaving[0]) * scale
            direction_y: float = (incoming[1] + leaving[1]) * scale
            outer_x: float = point[0] + direction_x * outer_reach
            outer_y: float = point[1] + direction_y * outer_reach
            inner_x: float = point[0] - direction_x * inner_reach
            inner_y: float = point[1] - direction_y * inner_reach
            outer_bottom.append(bm.verts.new((outer_x, outer_y, 0.0)))
            outer_top.append(bm.verts.new((outer_x, outer_y, height)))
            inner_bottom.append(bm.verts.new((inner_x, inner_y, 0.0)))
            inner_top.append(bm.verts.new((inner_x, inner_y, height)))

        # walking has the building on the left, so the outer edge is on the right of the walk
        for index in range(count):
            following: int = (index + 1) % count
            bm.faces.new([outer_top[index], outer_top[following], inner_top[following], inner_top[index]])
            bm.faces.new([inner_bottom[index], inner_bottom[following], outer_bottom[following], outer_bottom[index]])
            bm.faces.new([outer_bottom[index], outer_bottom[following], outer_top[following], outer_top[index]])
            bm.faces.new([inner_bottom[following], inner_bottom[index], inner_top[index], inner_top[following]])
        return bm
