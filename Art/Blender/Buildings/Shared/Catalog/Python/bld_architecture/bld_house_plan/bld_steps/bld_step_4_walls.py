# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 4: outline rings -> posts on the corners and walls on the segments."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import random

from bld_modules import TOLERANCE, BayWallModule, DiagonalWallModule, PillarModule, PostModule, WallModule

from ...bld_style import ModuleAtlas
from ..bld_house_plan import ModulePlacement, ModuleRing
from .bld_step_1_footprint import Side
from .bld_step_2_outline import OutlineRing, OutlineSegment
from .bld_step_4_wall_patterns import (
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

    def __init__(self, atlas: ModuleAtlas, min_post_spacing: float = 2.0) -> None:
        """Creates a wall filler.

        Args:
            atlas: Modules the filler may place.
            min_post_spacing: Smallest distance in m between two posts on a segment,
                corners included.

        Raises:
            ValueError: If the atlas contains no wall module.
        """
        self._atlas: ModuleAtlas = atlas
        self._min_post_spacing: float = min_post_spacing

        # one wall per width in cm, the atlas lists the first of equal widths first, bay walls are no filler
        self._walls_by_width: dict[int, WallModule] = {}
        for module in atlas.modules_of(WallModule):
            if isinstance(module, WallModule) and not isinstance(module, (BayWallModule, DiagonalWallModule)):
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
            if isinstance(module, PostModule) and not isinstance(module, PillarModule)
        ]
        if not posts:
            raise ValueError("The atlas contains no post module")
        corner_post: PostModule = posts[0]  # the atlas lists the widest first
        middle_post: PostModule = posts[-1]  # the narrowest, equal to the corner post if alone

        # a ring that touches itself on a point (two cells that only meet diagonally) has two
        # corners there, but only one post fits
        corner_points: list[tuple[float, float]] = list(
            dict.fromkeys((float(corner.point[0]), float(corner.point[1])) for corner in ring.corners)
        )
        placements: list[ModulePlacement] = [
            ModulePlacement(corner_post, point, 0) for point in corner_points
        ]
        for segment in ring.segments:
            placements.extend(self._fill_segment(segment, middle_post, random_source))
        return ModuleRing(tuple(placements))

    def _fill_segment(
        self, segment: OutlineSegment, middle_post: PostModule, random_source: random.Random
    ) -> list[ModulePlacement]:
        """Fills one straight segment with wall modules and posts between them.

        Args:
            segment: Segment to fill.
            middle_post: Post that stands between two walls.
            random_source: Random stream for the wall widths.

        Raises:
            ValueError: If the wall widths cannot add up to the segment length.

        Returns:
            Wall and post placements, the walls from the start to the end of the segment,
            the posts after them.
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

        for post_offset in self._post_offsets(widths, float(segment.length)):
            placements.append(
                ModulePlacement(
                    middle_post,
                    (
                        segment.start[0] + direction_x * post_offset,
                        segment.start[1] + direction_y * post_offset,
                    ),
                    0,
                )
            )
        return placements

    def _post_offsets(self, widths: WallPattern, length: float) -> list[float]:
        """Chooses the joints between two walls that get a post, mirrored around the middle.

        Args:
            widths: Wall widths in m in walking order.
            length: Segment length in m.

        Returns:
            Distances in m from the segment start, ascending. Only joints whose mirror
            image is a joint too are used, and neighbouring posts, the segment ends
            included, are at least min_post_spacing apart.
        """
        joints: list[float] = []
        offset: float = 0.0
        for width in widths[:-1]:
            offset += width
            joints.append(offset)

        def is_joint(distance: float) -> bool:
            return any(abs(joint - distance) <= TOLERANCE for joint in joints)

        half: float = length * 0.5
        has_center: bool = is_joint(half) and half >= self._min_post_spacing - TOLERANCE
        left_posts: list[float] = []
        for joint in joints:
            if joint >= half - TOLERANCE:
                break
            if not is_joint(length - joint):
                continue
            previous: float = left_posts[-1] if left_posts else 0.0
            if joint - previous >= self._min_post_spacing - TOLERANCE:
                left_posts.append(joint)

        # the innermost post and its mirror image (or the center post) must keep their distance
        while left_posts:
            gap: float = half - left_posts[-1] if has_center else length - 2 * left_posts[-1]
            if gap >= self._min_post_spacing - TOLERANCE:
                break
            left_posts.pop()

        offsets: list[float] = [*left_posts]
        if has_center:
            offsets.append(half)
        offsets.extend(length - post for post in reversed(left_posts))
        return offsets
