# Copyright (c) 2026 Emberfall. All Rights Reserved.

import random

from bld_modules import PostModule, WallModule

from .bld_contour import ContourRing, ContourSegment
from .bld_module_atlas import ModuleAtlas
from .bld_placement import Placement
from .bld_side import Side
from .bld_wall_ring import WallRing

# quarter turns so that the module front (-Y) faces outward
_ROTATION_STEPS: dict[Side, int] = {
    Side.SOUTH: 0,
    Side.EAST: 1,
    Side.NORTH: 2,
    Side.WEST: 3,
}
_TOLERANCE: float = 1e-9


class WallFiller:
    """Places posts on the corners and fills the segments of a ring with walls."""

    def __init__(self, atlas: ModuleAtlas) -> None:
        """Creates a wall filler.

        Args:
            atlas: Modules the filler may place.

        Returns:
            None.
        """
        self._atlas: ModuleAtlas = atlas
        return None

    def fill(self, ring: ContourRing, random_source: random.Random) -> WallRing:
        """Fills one contour ring.

        Args:
            ring: Contour to fill.
            random_source: Random stream for the wall widths.

        Raises:
            ValueError: If the atlas lacks a post or cannot fill a segment.

        Returns:
            Posts first, then the walls segment by segment in walking order.
        """
        posts: list[PostModule] = [
            module for module in self._atlas.modules_of(PostModule)
            if isinstance(module, PostModule)
        ]
        if not posts:
            raise ValueError("The atlas contains no post module")

        placements: list[Placement] = [
            Placement(posts[0], (float(corner.point[0]), float(corner.point[1])), 0)
            for corner in ring.corners
        ]
        for segment in ring.segments:
            placements.extend(self._fill_segment(segment, random_source))
        return WallRing(tuple(placements))

    def _fill_segment(
        self, segment: ContourSegment, random_source: random.Random
    ) -> list[Placement]:
        """Fills one straight segment with wall modules.

        Args:
            segment: Segment to fill.
            random_source: Random stream for the wall widths.

        Returns:
            Wall placements from the start to the end of the segment.
        """
        walls: list[WallModule] = [
            module for module in self._atlas.modules_of(WallModule)
            if isinstance(module, WallModule)
        ]
        direction_x: int = (segment.end[0] > segment.start[0]) - (segment.end[0] < segment.start[0])
        direction_y: int = (segment.end[1] > segment.start[1]) - (segment.end[1] < segment.start[1])
        rotation_steps: int = _ROTATION_STEPS[segment.outward]

        placements: list[Placement] = []
        offset: float = 0.0
        remaining: float = float(segment.length)

        while remaining > _TOLERANCE:
            fitting: list[WallModule] = [
                wall for wall in walls if wall.width <= remaining + _TOLERANCE
            ]
            if not fitting:
                raise ValueError(
                    f"No wall module fits the remaining {remaining} m of a segment "
                    f"from {segment.start} to {segment.end}"
                )
            # wider walls are likelier, but the split still varies
            wall: WallModule = random_source.choices(
                fitting, weights=[wall.width for wall in fitting]
            )[0]
            center: float = offset + wall.width * 0.5
            placements.append(
                Placement(
                    wall,
                    (
                        segment.start[0] + direction_x * center,
                        segment.start[1] + direction_y * center,
                    ),
                    rotation_steps,
                )
            )
            offset += wall.width
            remaining -= wall.width
        return placements
