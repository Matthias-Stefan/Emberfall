# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 3: outline rings -> posts on the corners and walls on the segments."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import random

from bld_modules import PostModule, WallModule

from ...bld_style import ModuleAtlas
from ..bld_house_plan import ModulePlacement, ModuleRing
from .bld_step_1_footprint import Side
from .bld_step_2_outline import OutlineRing, OutlineSegment
from .bld_step_3_wall_patterns import (
    WallPattern,
    WallPatternPicker,
    is_symmetric,
    max_neighbour_ratio,
    max_run_of,
)

# quarter turns so that the module front (-Y) faces outward
_ROTATION_STEPS: dict[Side, int] = {
    Side.SOUTH: 0,
    Side.EAST: 1,
    Side.NORTH: 2,
    Side.WEST: 3,
}


class WallFiller:
    """Places posts on the corners and fills the segments of a ring with walls."""

    def __init__(self, atlas: ModuleAtlas) -> None:
        """Creates a wall filler.

        Args:
            atlas: Modules the filler may place.

        Raises:
            ValueError: If the atlas contains no wall module.
        """
        self._atlas: ModuleAtlas = atlas

        # one wall per width in cm, the atlas lists the first of equal widths first
        self._walls_by_width: dict[int, WallModule] = {}
        for module in atlas.modules_of(WallModule):
            if isinstance(module, WallModule):
                self._walls_by_width.setdefault(round(module.width * 100), module)
        if not self._walls_by_width:
            raise ValueError("The atlas contains no wall module")

        # first symmetric, then no more than two 1 m walls in a row, never a jump above 2x
        self._pattern_picker: WallPatternPicker = WallPatternPicker(
            widths=[wall.width for wall in self._walls_by_width.values()],
            rules=[max_neighbour_ratio(2.0)],
            preferences=[is_symmetric, max_run_of(1.0, 2)],
        )

    def fill(self, ring: OutlineRing, random_source: random.Random) -> ModuleRing:
        """Fills one outline ring.

        Args:
            ring: Outline to fill.
            random_source: Random stream for the wall widths.

        Raises:
            ValueError: If the atlas lacks a post or the wall widths cannot fill a segment.

        Returns:
            Posts first, then the walls segment by segment in walking order.
        """
        posts: list[PostModule] = [
            module for module in self._atlas.modules_of(PostModule)
            if isinstance(module, PostModule)
        ]
        if not posts:
            raise ValueError("The atlas contains no post module")

        placements: list[ModulePlacement] = [
            ModulePlacement(posts[0], (float(corner.point[0]), float(corner.point[1])), 0)
            for corner in ring.corners
        ]
        for segment in ring.segments:
            placements.extend(self._fill_segment(segment, random_source))
        return ModuleRing(tuple(placements))

    def _fill_segment(
        self, segment: OutlineSegment, random_source: random.Random
    ) -> list[ModulePlacement]:
        """Fills one straight segment with wall modules.

        Args:
            segment: Segment to fill.
            random_source: Random stream for the wall widths.

        Raises:
            ValueError: If the wall widths cannot add up to the segment length.

        Returns:
            Wall placements from the start to the end of the segment.
        """
        widths: WallPattern = self._pattern_picker.pick(float(segment.length), random_source)
        direction_x: int = (segment.end[0] > segment.start[0]) - (segment.end[0] < segment.start[0])
        direction_y: int = (segment.end[1] > segment.start[1]) - (segment.end[1] < segment.start[1])
        rotation_steps: int = _ROTATION_STEPS[segment.outward]

        placements: list[ModulePlacement] = []
        offset: float = 0.0

        for width in widths:
            wall: WallModule = self._walls_by_width[round(width * 100)]
            center: float = offset + width * 0.5
            placements.append(
                ModulePlacement(
                    wall,
                    (
                        segment.start[0] + direction_x * center,
                        segment.start[1] + direction_y * center,
                    ),
                    rotation_steps,
                )
            )
            offset += width
        return placements
