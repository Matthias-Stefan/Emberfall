# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 9 helper: rings -> a straight wall turned into a half circle, the round end of a building."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import math
import random
from dataclasses import replace

from bld_modules import (
    TOLERANCE,
    ArcFloorModule,
    ArcWallModule,
    ArcWindowModule,
    DoorModule,
    PostModule,
    WallModule,
    WindowModule,
)

from ...bld_create_info import LevelsCreateInfo
from ...bld_style import ModuleAtlas
from ..bld_house_plan import FoundationPlan, ModulePlacement, ModuleRing
from .bld_step_1_footprint import Footprint
from .bld_step_2_outline import CornerKind, OutlineRing, OutlineSegment
from .bld_step_6_stairs import Rectangle, StairPlacer

Point = tuple[float, float]
Cell = tuple[int, int]

# front direction (-Y turned by n quarter turns) per rotation, the width axis is the next one
_FRONT: tuple[tuple[int, int], ...] = ((0, -1), (1, 0), (0, 1), (-1, 0))

# sides of the outline in the order of the rotations
_SIDES: tuple[str, ...] = ("south", "east", "north", "west")


class ApsisPlacer:
    """Turns a free straight wall into a half circle, on the ground floor and on the levels above."""

    def __init__(self, atlas: ModuleAtlas) -> None:
        """Creates an apsis placer.

        Args:
            atlas: Modules the placer may take measures from, a window gives the size of the openings.

        Returns:
            None.
        """
        self._atlas: ModuleAtlas = atlas
        return None

    def place_ground(
        self,
        rings: tuple[ModuleRing, ...],
        outlines: tuple[OutlineRing, ...],
        footprint: Footprint,
        foundation: FoundationPlan | None,
        obstacles: tuple[Rectangle, ...],
        levels_info: LevelsCreateInfo,
        random_source: random.Random,
    ) -> tuple[tuple[ModuleRing, ...], tuple[ModulePlacement, ...]]:
        """Turns one wall of the ground floor into a half circle.

        Args:
            rings are the finished rings of the ground floor, lifted onto the foundation.
            outlines are the outline rings the rings were filled from, same order.
            footprint is the footprint of the ground floor, the half circle keeps off its cells.
            foundation is the foundation of the building, None if it stands on the ground.
            obstacles are the areas of stairs and balconies the half circle must keep clear of.
            levels_info is the rules for the round ends.
            random_source is the random stream for the choices, separate from all other steps.

        Returns:
            The rings and the solid base under the half circle. Both unchanged and empty if the
            chance fails or no wall fits.
        """
        if levels_info.round_end_chance <= 0.0 or random_source.random() >= levels_info.round_end_chance:
            return rings, ()
        cells: frozenset[Cell] = footprint.main_cells.union(*footprint.extension_cells)
        candidates: list[tuple[int, OutlineSegment]] = [
            (ring_index, segment)
            for ring_index, (ring, outline) in enumerate(zip(rings, outlines))
            for segment in self._free_segments(ring, outline, cells, obstacles, levels_info)
        ]
        if not candidates:
            return rings, ()
        ring_index, segment = random_source.choice(candidates)

        on_segment: list[ModulePlacement] = self.on_segment(rings[ring_index], segment)
        template = next(
            placement.module for placement in on_segment if isinstance(placement.module, (WallModule, WindowModule))
        )
        with_windows: bool = random_source.random() < 0.8
        arc: ArcWallModule = self._arc_module(segment.length, template, with_windows)
        rotation: int = _SIDES.index(segment.outward.value)
        elevation: float = on_segment[0].elevation

        new_rings: list[ModuleRing] = list(rings)
        new_rings[ring_index] = self._swap(rings[ring_index], segment, arc, rotation, elevation)

        base: tuple[ModulePlacement, ...] = ()
        if foundation is not None:
            reach: float = foundation.wall_depth * 0.5 + foundation.overhang
            plinth: ArcFloorModule = ArcFloorModule(
                width=arc.width + 2.0 * reach,
                height=foundation.height,
                depth=arc.bulge + reach,
                segments=arc.segments,
            )
            base = (self._floor_of(plinth, segment, rotation, 0.0),)
        return tuple(new_rings), base

    def continue_up(
        self,
        ring: ModuleRing,
        outline: OutlineRing,
        lower_rings: tuple[ModuleRing, ...],
        wall_elevation: float,
        slab_elevation: float,
        slab_height: float,
    ) -> tuple[ModuleRing, tuple[ModulePlacement, ...]]:
        """Carries the half circles of the level below up, where the outline of the level still has them.

        Args:
            ring is the finished ring of the level, at the wall elevation.
            outline is the outline the ring was filled from.
            lower_rings are the rings of the level below.
            wall_elevation is the height of the wall bottoms of the level in m.
            slab_elevation is the height of the bottom of the floor slabs of the level in m.
            slab_height is the thickness of the floor slabs in m.

        Returns:
            The ring with the half circles and the floor slabs under them. Both unchanged and empty
            if the level has no wall on the same line as a half circle below.
        """
        floor: list[ModulePlacement] = []
        for lower_ring in lower_rings:
            for lower in lower_ring.placements:
                module = lower.module
                if not self.is_round_end(module):
                    continue
                segment: OutlineSegment | None = self._segment_of(lower, outline)
                if segment is None:
                    continue
                on_segment: list[ModulePlacement] = self.on_segment(ring, segment)
                walls = [placement for placement in on_segment if isinstance(placement.module, (WallModule, WindowModule))]
                if not walls:
                    continue
                arc: ArcWallModule = self._arc_module(
                    segment.length, walls[0].module, isinstance(module, ArcWindowModule)
                )
                ring = self._swap(ring, segment, arc, lower.rotation_steps, wall_elevation)
                reach: float = arc.depth * 0.5
                slab: ArcFloorModule = ArcFloorModule(
                    width=arc.width + 2.0 * reach,
                    height=slab_height,
                    depth=arc.bulge + reach,
                    segments=arc.segments,
                )
                floor.append(self._floor_of(slab, segment, lower.rotation_steps, slab_elevation))
        return ring, tuple(floor)

    @staticmethod
    def is_round_end(module: object) -> bool:
        """Tests whether a module is the curved wall of a round end.

        Args:
            module is the module to test.

        Returns:
            @c True if it is a curved wall that is a half circle at least two meters wide, the
            curved walls of bays are shallower, otherwise @c False.
        """
        return (
            isinstance(module, ArcWallModule)
            and module.width >= 2.0 - TOLERANCE
            and module.bulge >= module.width * 0.5 - TOLERANCE
        )

    def _free_segments(
        self,
        ring: ModuleRing,
        outline: OutlineRing,
        cells: frozenset[Cell],
        obstacles: tuple[Rectangle, ...],
        levels_info: LevelsCreateInfo,
    ) -> list[OutlineSegment]:
        """Collects the segments of an outline that may become a half circle.

        Args:
            ring is the ring of the outline.
            outline is the outline ring.
            cells are the cells of the footprint.
            obstacles are the areas of stairs and balconies.
            levels_info is the rules for the round ends, they limit the length.

        Returns:
            The segments between two outer corners, of an allowed length, without a door and
            with nothing in the way of the half circle.
        """
        segments: list[OutlineSegment] = []
        corner_count: int = len(outline.corners)
        for index, segment in enumerate(outline.segments):
            if (
                outline.corners[index].kind is not CornerKind.OUTER
                or outline.corners[(index + 1) % corner_count].kind is not CornerKind.OUTER
                or not levels_info.round_end_min_length <= segment.length <= levels_info.round_end_max_length
            ):
                continue
            on_segment: list[ModulePlacement] = self.on_segment(ring, segment)
            if not any(isinstance(placement.module, (WallModule, WindowModule)) for placement in on_segment):
                continue
            if any(isinstance(placement.module, DoorModule) for placement in on_segment):
                continue
            if any(isinstance(placement.module, ArcWallModule) for placement in on_segment):
                continue
            area: Rectangle = self._area_of(segment, on_segment[0].module.depth)
            if any(StairPlacer.overlaps(area, obstacle) for obstacle in obstacles):
                continue
            if any(StairPlacer.overlaps(area, (cell_x, cell_y, cell_x + 1.0, cell_y + 1.0)) for cell_x, cell_y in cells):
                continue
            segments.append(segment)
        return segments

    @staticmethod
    def _area_of(segment: OutlineSegment, wall_depth: float) -> Rectangle:
        """Measures the area the half circle of a segment needs, from the wall line outward.

        Args:
            segment is the segment.
            wall_depth is the wall thickness in m.

        Returns:
            The rectangle in m, wide as the segment and as deep as the half circle with its wall and base.
        """
        reach: float = segment.length * 0.5 + wall_depth * 0.5 + 0.1
        normal: tuple[int, int] = _FRONT[_SIDES.index(segment.outward.value)]
        along_min_x: float = min(segment.start[0], segment.end[0])
        along_max_x: float = max(segment.start[0], segment.end[0])
        along_min_y: float = min(segment.start[1], segment.end[1])
        along_max_y: float = max(segment.start[1], segment.end[1])
        return (
            along_min_x + min(0.0, normal[0] * reach),
            along_min_y + min(0.0, normal[1] * reach),
            along_max_x + max(0.0, normal[0] * reach),
            along_max_y + max(0.0, normal[1] * reach),
        )

    @staticmethod
    def on_segment(ring: ModuleRing, segment: OutlineSegment) -> list[ModulePlacement]:
        """Collects the walls, windows, doors and middle posts that stand on a segment.

        Args:
            ring is the ring to search.
            segment is the segment, its corner posts at the ends are left out.

        Returns:
            The placements on the segment in ring order, the stairs in front of it are left out.
        """
        horizontal: bool = abs(segment.start[1] - segment.end[1]) <= TOLERANCE
        line: float = segment.start[1] if horizontal else segment.start[0]
        low: float = min(segment.start[0], segment.end[0]) if horizontal else min(segment.start[1], segment.end[1])
        high: float = max(segment.start[0], segment.end[0]) if horizontal else max(segment.start[1], segment.end[1])
        found: list[ModulePlacement] = []
        for placement in ring.placements:
            if not isinstance(placement.module, (WallModule, PostModule, WindowModule, DoorModule)):
                continue
            across: float = placement.position[1] if horizontal else placement.position[0]
            along: float = placement.position[0] if horizontal else placement.position[1]
            if abs(across - line) <= TOLERANCE and low + TOLERANCE < along < high - TOLERANCE:
                found.append(placement)
        return found

    def _segment_of(self, arc: ModulePlacement, outline: OutlineRing) -> OutlineSegment | None:
        """Finds the segment of an outline that lies on the chord of a half circle.

        Args:
            arc is the curved wall of the level below.
            outline is the outline of the level.

        Returns:
            The segment with the same ends and the same outward side, @c None if there is none.
        """
        tangent: tuple[int, int] = _FRONT[(arc.rotation_steps + 1) % 4]
        half: float = arc.module.width * 0.5
        ends: list[Point] = [
            (arc.position[0] - tangent[0] * half, arc.position[1] - tangent[1] * half),
            (arc.position[0] + tangent[0] * half, arc.position[1] + tangent[1] * half),
        ]
        for segment in outline.segments:
            if segment.outward.value != _SIDES[arc.rotation_steps]:
                continue
            points: list[Point] = [(float(segment.start[0]), float(segment.start[1])), (float(segment.end[0]), float(segment.end[1]))]
            if all(any(math.dist(point, end) <= TOLERANCE for end in ends) for point in points):
                return segment
        return None

    def _arc_module(self, length: float, template: WallModule, with_windows: bool) -> ArcWallModule:
        """Creates the curved wall for a half circle.

        Args:
            length is the length of the segment in m, it becomes the width of the half circle.
            template is a wall of the segment, it gives height and thickness.
            with_windows is whether the curved wall gets openings.

        Returns:
            A half circle as wide as the segment, with windows if the atlas has a window to measure
            them from, otherwise a plain wall.
        """
        segments: int = max(8, round(length * 6.0))
        windows: list[WindowModule] = [
            module for module in self._atlas.modules_of(WindowModule) if isinstance(module, WindowModule)
        ]
        if with_windows and windows:
            sections: int = max(1, round(length / 1.5))
            section_width: float = length / sections
            return ArcWindowModule(
                width=float(length),
                height=template.height,
                depth=template.depth,
                bulge=length * 0.5,
                segments=segments,
                opening_width=min(windows[-1].opening_width, section_width * 0.55),
                opening_height=windows[-1].opening_height,
                sill_height=windows[-1].sill_height,
                opening_count=sections,
            )
        return ArcWallModule(
            width=float(length), height=template.height, depth=template.depth, bulge=length * 0.5, segments=segments
        )

    @staticmethod
    def _swap(
        ring: ModuleRing,
        segment: OutlineSegment,
        arc: ArcWallModule,
        rotation: int,
        elevation: float,
    ) -> ModuleRing:
        """Replaces everything on a segment by one curved wall.

        Args:
            ring is the ring to edit.
            segment is the segment that becomes the half circle.
            arc is the curved wall.
            rotation is the rotation of the curved wall, its front looks outward.
            elevation is the height of the bottom of the curved wall in m.

        Returns:
            The ring without the walls, windows and middle posts of the segment, with the curved wall at the end.
        """
        removed: list[ModulePlacement] = ApsisPlacer.on_segment(ring, segment)
        kept: list[ModulePlacement] = [placement for placement in ring.placements if placement not in removed]
        middle: Point = (
            (segment.start[0] + segment.end[0]) * 0.5,
            (segment.start[1] + segment.end[1]) * 0.5,
        )
        kept.append(ModulePlacement(arc, middle, rotation, elevation))
        return ModuleRing(tuple(kept))

    @staticmethod
    def _floor_of(
        slab: ArcFloorModule, segment: OutlineSegment, rotation: int, elevation: float
    ) -> ModulePlacement:
        """Places a half circle slab so its chord lies on the wall line.

        Args:
            slab is the slab.
            segment is the segment the half circle stands on.
            rotation is the rotation of the half circle, its front looks outward.
            elevation is the height of the slab bottom in m.

        Returns:
            The placement, the slab is centered in depth, so it is moved half its depth outward.
        """
        normal: tuple[int, int] = _FRONT[rotation]
        middle: Point = (
            (segment.start[0] + segment.end[0]) * 0.5,
            (segment.start[1] + segment.end[1]) * 0.5,
        )
        return ModulePlacement(
            slab,
            (middle[0] + normal[0] * slab.depth * 0.5, middle[1] + normal[1] * slab.depth * 0.5),
            rotation,
            elevation,
        )
