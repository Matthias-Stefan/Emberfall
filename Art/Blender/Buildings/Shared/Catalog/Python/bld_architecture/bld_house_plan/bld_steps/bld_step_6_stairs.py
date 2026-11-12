# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 6: rings on a foundation -> rings with a stair in front of every door."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import random

from bld_modules import TOLERANCE, DoorModule, PostModule, StairModule

from ...bld_style import ModuleAtlas
from ..bld_house_plan import FoundationPlan, ModulePlacement, ModuleRing

Rectangle = tuple[float, float, float, float]
"""Axis-aligned area as min X, min Y, max X, max Y in m."""

# outward direction per quarter turn, the module front (-Y) turned counter-clockwise
_OUTWARD: tuple[tuple[int, int], ...] = ((0, -1), (1, 0), (0, 1), (-1, 0))


class StairPlacer:
    """Puts a stair in front of every door so the foundation can be climbed."""

    def __init__(self, atlas: ModuleAtlas) -> None:
        """Creates a stair placer.

        Args:
            atlas: Stairs the placer may choose from.

        Returns:
            None.
        """
        self._atlas: ModuleAtlas = atlas
        return None

    def place(
        self,
        rings: tuple[ModuleRing, ...],
        foundation: FoundationPlan | None,
        random_source: random.Random,
    ) -> tuple[ModuleRing, ...]:
        """Adds a stair to every door that has a fitting stair and free space.

        Args:
            rings: Rings with posts, walls and openings, lifted onto the foundation.
            foundation: Foundation the stairs climb, None means no stairs are needed.
            random_source: Random stream for the stair variants, separate from all other steps.

        Returns:
            The rings with the stairs appended to the ring of their door, in walking order.
            A door without a stair of its width and the foundation height stays without one.
        """
        if foundation is None:
            return rings

        occupied: list[Rectangle] = self._band_rectangles(rings, foundation, None)

        placed_rings: list[ModuleRing] = []
        for ring in rings:
            stairs: list[ModulePlacement] = []
            for placement in ring.placements:
                if not isinstance(placement.module, DoorModule):
                    continue
                candidates: list[StairModule] = self._find_stairs(placement.module.width, foundation)
                if not candidates:
                    continue
                stair: ModulePlacement = self._stair_in_front_of(
                    placement, random_source.choice(candidates), foundation
                )
                stair_rectangle: Rectangle = StairPlacer.rectangle_of(
                    stair, stair.module.width, stair.module.depth
                )
                if any(StairPlacer.overlaps(stair_rectangle, other) for other in occupied):
                    continue
                occupied.append(stair_rectangle)
                stairs.append(stair)
            placed_rings.append(ModuleRing((*ring.placements, *stairs)))
        return tuple(placed_rings)

    def has_room(
        self,
        wall: ModulePlacement,
        rings: tuple[ModuleRing, ...],
        foundation: FoundationPlan | None,
    ) -> bool:
        """Tests whether a door in this wall slot could get a stair in front of it.

        Args:
            wall is the wall slot that may become a door.
            rings are the rings with posts and walls, before the openings are placed.
            foundation is the foundation the stair would climb, None means no stair is needed.

        Returns:
            True if no stair is needed or one of the right width fits without hitting other modules,
            otherwise False.
        """
        if foundation is None:
            return True
        candidates: list[StairModule] = self._find_stairs(wall.module.width, foundation)
        if not candidates:
            return False
        stair: ModulePlacement = self._stair_in_front_of(wall, candidates[0], foundation)
        stair_rectangle: Rectangle = StairPlacer.rectangle_of(
            stair, stair.module.width, stair.module.depth
        )
        return not any(
            StairPlacer.overlaps(stair_rectangle, other)
            for other in self._band_rectangles(rings, foundation, wall)
        )

    def _band_rectangles(
        self,
        rings: tuple[ModuleRing, ...],
        foundation: FoundationPlan,
        ignored: ModulePlacement | None,
    ) -> list[Rectangle]:
        """Collects the foundation band area under every wall and post.

        Args:
            rings are the rings to collect from.
            foundation is the foundation, provides wall depth and overhang.
            ignored is a placement to leave out, None leaves out nothing.

        Returns:
            One area per wall or post, doors and stairs are left out.
        """
        band_depth: float = foundation.wall_depth + 2.0 * foundation.overhang
        return [
            StairPlacer.rectangle_of(
                placement,
                # a post is thicker than a wall but still inside the band, so it counts as band depth
                band_depth
                if isinstance(placement.module, PostModule)
                else placement.module.width + 2.0 * foundation.overhang,
                band_depth,
            )
            for ring in rings
            for placement in ring.placements
            if placement is not ignored
            and not isinstance(placement.module, (DoorModule, StairModule))
        ]

    def _find_stairs(self, width: float, foundation: FoundationPlan) -> list[StairModule]:
        """Finds all stairs that fit a door width and the foundation.

        Args:
            width is the door width in m.
            foundation is the foundation the stair has to climb.

        Returns:
            Atlas stairs as wide as the door and as high as the foundation, empty if none fits.
        """
        return [
            module
            for module in self._atlas.modules_of(StairModule)
            if isinstance(module, StairModule)
            and abs(module.width - width) <= TOLERANCE
            and abs(module.height - foundation.height) <= TOLERANCE
        ]

    @staticmethod
    def _stair_in_front_of(
        door: ModulePlacement, stair: StairModule, foundation: FoundationPlan
    ) -> ModulePlacement:
        """Places a stair with its top step against the foundation, centered on the door.

        Args:
            door is the placement of the door.
            stair is the stair module to place.
            foundation is the foundation, its outer edge is where the stair starts.

        Returns:
            Stair placement on the ground, turned like the door.
        """
        distance: float = foundation.wall_depth * 0.5 + foundation.overhang + stair.depth * 0.5
        direction: tuple[int, int] = _OUTWARD[door.rotation_steps % 4]
        position: tuple[float, float] = (
            door.position[0] + direction[0] * distance,
            door.position[1] + direction[1] * distance,
        )
        return ModulePlacement(stair, position, door.rotation_steps, 0.0)

    @staticmethod
    def rectangle_of(placement: ModulePlacement, width: float, depth: float) -> Rectangle:
        """Computes the area of a placed module seen from above.

        Args:
            placement is the placed module, provides center and quarter turns.
            width is the extent along the module X axis in m.
            depth is the extent along the module Y axis in m.

        Returns:
            Area in m, quarter turns swap width and depth.
        """
        half_x: float = width * 0.5
        half_y: float = depth * 0.5
        if placement.rotation_steps % 2 == 1:
            half_x, half_y = half_y, half_x
        return (
            placement.position[0] - half_x,
            placement.position[1] - half_y,
            placement.position[0] + half_x,
            placement.position[1] + half_y,
        )

    @staticmethod
    def overlaps(first: Rectangle, second: Rectangle) -> bool:
        """Tests whether two areas share space, touching edges do not count.

        Args:
            first is the first area.
            second is the second area.

        Returns:
            True if the areas overlap by more than the tolerance, otherwise False.
        """
        return (
            first[0] < second[2] - TOLERANCE
            and second[0] < first[2] - TOLERANCE
            and first[1] < second[3] - TOLERANCE
            and second[1] < first[3] - TOLERANCE
        )
