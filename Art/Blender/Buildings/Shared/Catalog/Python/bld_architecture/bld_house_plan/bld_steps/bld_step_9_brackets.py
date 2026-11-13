# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 9 helper: ring with bays and the rings below -> braces under the bays."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import math

from bld_modules import (
    TOLERANCE,
    ArcWallModule,
    BayWallModule,
    BracketModule,
    WallModule,
    WindowModule,
)

from ...bld_style import ModuleAtlas
from ..bld_house_plan import ModulePlacement, ModuleRing
from .bld_step_6_stairs import StairPlacer

Point = tuple[float, float]

# front direction (-Y turned by n quarter turns) per rotation, the width axis is the next one
_FRONT: tuple[tuple[int, int], ...] = ((0, -1), (1, 0), (0, 1), (-1, 0))


class BracketPlacer:
    """Puts diagonal braces under the bays of a level, where a wall of the level below carries them."""

    def __init__(self, atlas: ModuleAtlas) -> None:
        """Creates a bracket placer.

        Args:
            atlas: Modules the placer may use, the brackets must be as wide as the bays reach out.

        Returns:
            None.
        """
        self._atlas: ModuleAtlas = atlas
        return None

    def place(
        self,
        ring: ModuleRing,
        lower_rings: tuple[ModuleRing, ...],
        slab_elevation: float,
    ) -> tuple[ModulePlacement, ...]:
        """Places the braces under all bays of a ring.

        Args:
            ring is the ring of the level with its bays.
            lower_rings are the rings of the level below, the braces stand on their walls.
            slab_elevation is the height of the bottom of the floor slabs of the level in m.

        Returns:
            The braces, empty if the atlas has no bracket or no wall of the level below lies under a bay.
        """
        brackets: list[BracketModule] = [
            module for module in self._atlas.modules_of(BracketModule) if isinstance(module, BracketModule)
        ]
        if not brackets:
            return ()
        supports: list[ModulePlacement] = [
            placement
            for lower_ring in lower_rings
            for placement in lower_ring.placements
            if not isinstance(placement.module, (BayWallModule, BracketModule))
            and hasattr(placement.module, "depth")
        ]
        rectangles: list[tuple[float, float, float, float]] = [
            StairPlacer.rectangle_of(placement, placement.module.width, placement.module.depth)
            for placement in supports
        ]

        side_walls: list[ModulePlacement] = [
            placement
            for placement in ring.placements
            if isinstance(placement.module, BayWallModule) and not isinstance(placement.module, ArcWallModule)
        ]

        # anchor on the wall line, index of the direction the brace points to, reach in m
        anchors: list[tuple[Point, int, float]] = []
        for placement in ring.placements:
            module = placement.module
            if isinstance(module, ArcWallModule):
                tangent: tuple[int, int] = _FRONT[(placement.rotation_steps + 1) % 4]
                offsets: list[tuple[float, float]] = [(0.0, module.bulge)]
                if module.width >= 2.0 - TOLERANCE:
                    offsets.extend([(-0.5, 0.4), (0.5, 0.4)])
                for offset, reach in offsets:
                    anchors.append(
                        (
                            (
                                placement.position[0] + tangent[0] * offset,
                                placement.position[1] + tangent[1] * offset,
                            ),
                            placement.rotation_steps,
                            reach,
                        )
                    )
            elif isinstance(module, (WallModule, WindowModule)) and not isinstance(module, BayWallModule):
                anchors.extend(self._straight_bay_anchors(placement, side_walls))

        placements: list[ModulePlacement] = []
        for anchor, direction, reach in anchors:
            bracket: BracketModule | None = self._bracket_of(brackets, reach)
            if bracket is None or not self._is_covered(anchor, rectangles):
                continue
            normal: tuple[int, int] = _FRONT[direction]
            placements.append(
                ModulePlacement(
                    bracket,
                    (anchor[0] + normal[0] * bracket.width * 0.5, anchor[1] + normal[1] * bracket.width * 0.5),
                    # the high end (+X) must point away from the wall
                    (direction + 3) % 4,
                    slab_elevation - bracket.height,
                )
            )
        return tuple(placements)

    @staticmethod
    def _straight_bay_anchors(
        front: ModulePlacement, side_walls: list[ModulePlacement]
    ) -> list[tuple[Point, int, float]]:
        """Finds the anchors of a straight bay if a wall is its front.

        A wall is the front of a bay if a side wall stands behind each of its ends, a wall that
        only has neighbors on the wall line has none.

        Args:
            front is the wall or window to test.
            side_walls are the side walls of all bays of the ring.

        Returns:
            The two anchors on the wall line, each with the direction index of the bay and its reach,
            empty if the wall is no bay front.
        """
        normal: tuple[int, int] = _FRONT[front.rotation_steps]
        tangent: tuple[int, int] = _FRONT[(front.rotation_steps + 1) % 4]
        anchors: list[tuple[Point, int, float]] = []
        for sign in (-1, 1):
            for side in side_walls:
                expected: Point = (
                    front.position[0] + sign * tangent[0] * front.module.width * 0.5 - normal[0] * side.module.width * 0.5,
                    front.position[1] + sign * tangent[1] * front.module.width * 0.5 - normal[1] * side.module.width * 0.5,
                )
                if math.dist(side.position, expected) <= TOLERANCE:
                    inner_end: Point = (
                        side.position[0] - normal[0] * side.module.width * 0.5,
                        side.position[1] - normal[1] * side.module.width * 0.5,
                    )
                    anchors.append((inner_end, front.rotation_steps, side.module.width))
                    break
        return anchors if len(anchors) == 2 else []

    @staticmethod
    def _bracket_of(brackets: list[BracketModule], reach: float) -> BracketModule | None:
        """Picks the bracket that reaches out as far as a bay.

        Args:
            brackets are the brackets of the atlas.
            reach is the distance in m the bay sticks out from the wall.

        Returns:
            The bracket whose projection is within 2 cm of the reach, @c None if there is none.
        """
        for bracket in brackets:
            if abs(bracket.width - reach) <= 0.02:
                return bracket
        return None

    @staticmethod
    def _is_covered(point: Point, rectangles: list[tuple[float, float, float, float]]) -> bool:
        """Tests whether a point lies on a wall or post of the level below.

        Args:
            point is the point in m.
            rectangles are the areas of the walls and posts below.

        Returns:
            @c True if one of them contains the point, otherwise @c False.
        """
        return any(
            min_x - TOLERANCE <= point[0] <= max_x + TOLERANCE
            and min_y - TOLERANCE <= point[1] <= max_y + TOLERANCE
            for min_x, min_y, max_x, max_y in rectangles
        )
