# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Builds the foundation band of a house, one closed mesh per outline ring."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import bmesh

from bld_architecture import FoundationPlan, OutlineRing, Side

# outward unit normal per side, Y points up in cell space
_NORMALS: dict[Side, tuple[int, int]] = {
    Side.NORTH: (0, 1),
    Side.EAST: (1, 0),
    Side.SOUTH: (0, -1),
    Side.WEST: (-1, 0),
}


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

        The band reaches from the inside of the wall plus the overhang to the outside of the wall
        plus the overhang, so it sticks out on both sides of the wall.

        Args:
            ring_index: Index of the ring in the plan.

        Returns:
            A new BMesh in m, outline points are grid points, floor at Z = 0.
            The caller owns it and must call free() on it.
        """
        ring: OutlineRing = self._foundation.outlines[ring_index]
        reach: float = self._foundation.wall_depth * 0.5 + self._foundation.overhang
        height: float = self._foundation.height

        bm: bmesh.types.BMesh = bmesh.new()
        outer_bottom: list[bmesh.types.BMVert] = []
        outer_top: list[bmesh.types.BMVert] = []
        inner_bottom: list[bmesh.types.BMVert] = []
        inner_top: list[bmesh.types.BMVert] = []

        count: int = len(ring.corners)
        for corner_index, corner in enumerate(ring.corners):
            # both walls at a corner are perpendicular, their normals add up to the diagonal
            incoming: tuple[int, int] = _NORMALS[ring.segments[corner_index - 1].outward]
            leaving: tuple[int, int] = _NORMALS[ring.segments[corner_index].outward]
            shift_x: float = (incoming[0] + leaving[0]) * reach
            shift_y: float = (incoming[1] + leaving[1]) * reach
            point_x: float = corner.point[0]
            point_y: float = corner.point[1]
            outer_bottom.append(bm.verts.new((point_x + shift_x, point_y + shift_y, 0.0)))
            outer_top.append(bm.verts.new((point_x + shift_x, point_y + shift_y, height)))
            inner_bottom.append(bm.verts.new((point_x - shift_x, point_y - shift_y, 0.0)))
            inner_top.append(bm.verts.new((point_x - shift_x, point_y - shift_y, height)))

        # walking has the building on the left, so the outer edge is on the right of the walk
        for index in range(count):
            following: int = (index + 1) % count
            bm.faces.new([outer_top[index], outer_top[following], inner_top[following], inner_top[index]])
            bm.faces.new([inner_bottom[index], inner_bottom[following], outer_bottom[following], outer_bottom[index]])
            bm.faces.new([outer_bottom[index], outer_bottom[following], outer_top[following], outer_top[index]])
            bm.faces.new([inner_bottom[following], inner_bottom[index], inner_top[index], inner_top[following]])
        return bm
