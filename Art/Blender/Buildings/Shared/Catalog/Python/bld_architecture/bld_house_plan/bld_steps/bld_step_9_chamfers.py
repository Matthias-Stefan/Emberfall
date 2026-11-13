# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 9 helper: rings -> outer corners cut off at 45 degrees, on the ground floor and the levels above."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import math
import random
from dataclasses import replace

from bld_modules import (
    TOLERANCE,
    ArcWallModule,
    DiagonalWallModule,
    DiagonalWindowModule,
    DoorModule,
    FloorModule,
    PostModule,
    TriangleFloorModule,
    WallModule,
    WindowModule,
)

from ...bld_create_info import LevelsCreateInfo
from ...bld_style import ModuleAtlas
from ..bld_house_plan import CornerCut, ModulePlacement, ModuleRing
from .bld_step_1_footprint import Footprint
from .bld_step_2_outline import CornerKind, OutlineRing, OutlineSegment
from .bld_step_9_apsis import ApsisPlacer

Point = tuple[float, float]
Cell = tuple[int, int]

# front direction (-Y turned by n quarter turns) per rotation
_FRONT: tuple[tuple[int, int], ...] = ((0, -1), (1, 0), (0, 1), (-1, 0))

# sides of the outline in the order of the rotations
_SIDES: tuple[str, ...] = ("south", "east", "north", "west")


class ChamferPlacer:
    """Cuts outer corners off at 45 degrees: a diagonal wall instead of the corner, half cells in the floor."""

    def __init__(self, atlas: ModuleAtlas) -> None:
        """Creates a chamfer placer.

        Args:
            atlas: Modules the placer may take measures from, a post and a window.

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
        levels_info: LevelsCreateInfo,
        random_source: random.Random,
    ) -> tuple[tuple[ModuleRing, ...], tuple[CornerCut, ...]]:
        """Cuts some outer corners of the ground floor.

        Args:
            rings are the finished rings of the ground floor, lifted onto the foundation.
            outlines are the outline rings the rings were filled from, same order.
            footprint is the footprint of the ground floor.
            levels_info is the rules for the chamfers.
            random_source is the random stream for the choices, separate from all other steps.

        Returns:
            The rings with the diagonal walls and the cuts. Both unchanged and empty if the chance
            fails or no corner fits.
        """
        if levels_info.chamfer_chance <= 0.0 or levels_info.max_chamfers == 0:
            return rings, ()
        cells: frozenset[Cell] = footprint.main_cells.union(*footprint.extension_cells)
        candidates: list[tuple[int, int]] = [
            (ring_index, corner_index)
            for ring_index, outline in enumerate(outlines)
            for corner_index, corner in enumerate(outline.corners)
            if corner.kind is CornerKind.OUTER
        ]
        random_source.shuffle(candidates)

        new_rings: list[ModuleRing] = list(rings)
        cuts: list[CornerCut] = []
        for ring_index, corner_index in candidates:
            if len(cuts) >= levels_info.max_chamfers:
                break
            if random_source.random() >= levels_info.chamfer_chance:
                continue
            sizes: list[int] = list(range(1, levels_info.max_chamfer_size + 1))
            random_source.shuffle(sizes)
            with_window: bool = random_source.random() < 0.5
            for size in sizes:
                cut: CornerCut | None = self._cut_of(outlines[ring_index], corner_index, size)
                if cut is None or not self._cells_free(cut, cells, frozenset()):
                    continue
                swapped: ModuleRing | None = self._swap(new_rings[ring_index], outlines[ring_index], cut, with_window)
                if swapped is not None:
                    new_rings[ring_index] = swapped
                    cuts.append(cut)
                    break
        return tuple(new_rings), tuple(cuts)

    def continue_up(
        self,
        ring: ModuleRing,
        outline: OutlineRing,
        lower_rings: tuple[ModuleRing, ...],
        cells: frozenset[Cell],
        blocked_cells: frozenset[Cell],
        random_source: random.Random,
    ) -> tuple[ModuleRing, tuple[CornerCut, ...]]:
        """Carries the cut corners of the level below up, where the level still has the corner.

        Args:
            ring is the finished ring of the level, at the wall elevation.
            outline is the outline the ring was filled from.
            lower_rings are the rings of the level below.
            cells are the cells of the level.
            blocked_cells are cells that must stay whole, where the stair comes through or lands.
            random_source is the random stream for the windows.

        Returns:
            The ring with the diagonal walls and the cuts. Both unchanged and empty if no corner of the
            level below is still a corner with room for the cut.
        """
        cuts: list[CornerCut] = []
        for lower in self.cuts_of(lower_rings):
            for corner_index, corner in enumerate(outline.corners):
                if corner.kind is not CornerKind.OUTER or (float(corner.point[0]), float(corner.point[1])) != lower.point:
                    continue
                cut: CornerCut | None = self._cut_of(outline, corner_index, lower.size)
                if cut is None or cut.rotation != lower.rotation or not self._cells_free(cut, cells, blocked_cells):
                    continue
                swapped: ModuleRing | None = self._swap(ring, outline, cut, random_source.random() < 0.5)
                if swapped is not None:
                    ring = swapped
                    cuts.append(cut)
        return ring, tuple(cuts)

    def cut_floor(
        self, floor: tuple[ModulePlacement, ...], cuts: tuple[CornerCut, ...]
    ) -> tuple[ModulePlacement, ...]:
        """Takes the cut cells out of a floor, a half slab stays where a cell is halved.

        Args:
            floor are the slabs of a level.
            cuts are the cut corners of the level.

        Returns:
            The floor without the cut-off cells, the halved cells carry a triangular slab.
        """
        result: list[ModulePlacement] = list(floor)
        for cut in cuts:
            leg_u, leg_v = self._legs(cut.rotation)
            for step_u in range(cut.size):
                for step_v in range(cut.size):
                    if step_u + step_v > cut.size - 1:
                        continue
                    center: Point = (
                        cut.point[0] + (step_u + 0.5) * leg_u[0] + (step_v + 0.5) * leg_v[0],
                        cut.point[1] + (step_u + 0.5) * leg_u[1] + (step_v + 0.5) * leg_v[1],
                    )
                    for placement in result:
                        if (
                            type(placement.module) is FloorModule
                            and math.dist(placement.position, center) <= TOLERANCE
                            and abs(placement.module.width - 1.0) <= TOLERANCE
                            and abs(placement.module.depth - 1.0) <= TOLERANCE
                        ):
                            result.remove(placement)
                            if step_u + step_v == cut.size - 1:
                                half: TriangleFloorModule = TriangleFloorModule(
                                    width=placement.module.width,
                                    height=placement.module.height,
                                    depth=placement.module.depth,
                                )
                                result.append(replace(placement, module=half, rotation_steps=cut.rotation))
                            break
        return tuple(result)

    @staticmethod
    def cuts_of(rings: tuple[ModuleRing, ...]) -> tuple[CornerCut, ...]:
        """Reads the cut corners from the diagonal walls of some rings.

        Args:
            rings are the rings to read.

        Returns:
            One cut per diagonal wall.
        """
        cuts: list[CornerCut] = []
        for ring in rings:
            for placement in ring.placements:
                module = placement.module
                if not isinstance(module, DiagonalWallModule):
                    continue
                size: int = round(module.width / math.sqrt(2.0))
                diagonal_x: int = _FRONT[placement.rotation_steps][0] + _FRONT[(placement.rotation_steps + 1) % 4][0]
                diagonal_y: int = _FRONT[placement.rotation_steps][1] + _FRONT[(placement.rotation_steps + 1) % 4][1]
                cuts.append(
                    CornerCut(
                        (
                            placement.position[0] + diagonal_x * size * 0.5,
                            placement.position[1] + diagonal_y * size * 0.5,
                        ),
                        size,
                        placement.rotation_steps,
                    )
                )
        return tuple(cuts)

    @staticmethod
    def cells_of(cuts: tuple[CornerCut, ...]) -> frozenset[Cell]:
        """Collects the cells that are cut or halved.

        Args:
            cuts are the cut corners.

        Returns:
            The cells in grid coordinates.
        """
        cells: set[Cell] = set()
        for cut in cuts:
            leg_u, leg_v = ChamferPlacer._legs(cut.rotation)
            for step_u in range(cut.size):
                for step_v in range(cut.size - step_u):
                    center_x: float = cut.point[0] + (step_u + 0.5) * leg_u[0] + (step_v + 0.5) * leg_v[0]
                    center_y: float = cut.point[1] + (step_u + 0.5) * leg_u[1] + (step_v + 0.5) * leg_v[1]
                    cells.add((math.floor(center_x), math.floor(center_y)))
        return frozenset(cells)

    @staticmethod
    def _legs(rotation: int) -> tuple[tuple[int, int], tuple[int, int]]:
        """Gives the directions that lead away from the corner along its two walls.

        Args:
            rotation is the rotation of the corner.

        Returns:
            The direction back along the wall that ends in the corner, then the direction along the wall that leaves it.
        """
        incoming: tuple[int, int] = _FRONT[(rotation + 1) % 4]
        return (-incoming[0], -incoming[1]), _FRONT[(rotation + 2) % 4]

    def _cut_of(self, outline: OutlineRing, corner_index: int, size: int) -> CornerCut | None:
        """Describes the cut of one outer corner.

        Args:
            outline is the outline ring of the corner.
            corner_index is the index of the corner in the ring.
            size is the length of the legs of the cut in m.

        Returns:
            The cut, @c None if a wall at the corner is shorter than the cut plus one meter.
        """
        incoming: OutlineSegment = outline.segments[corner_index - 1]
        leaving: OutlineSegment = outline.segments[corner_index]
        rotation: int = _SIDES.index(incoming.outward.value)
        if _SIDES.index(leaving.outward.value) != (rotation + 1) % 4:
            return None
        if incoming.length < size + 1 or leaving.length < size + 1:
            return None
        point = outline.corners[corner_index].point
        return CornerCut((float(point[0]), float(point[1])), size, rotation)

    def _cells_free(self, cut: CornerCut, cells: frozenset[Cell], blocked_cells: frozenset[Cell]) -> bool:
        """Tests whether all cells of a cut belong to the level and none of them must stay whole.

        Args:
            cut is the cut.
            cells are the cells of the level.
            blocked_cells are cells that must stay whole.

        Returns:
            @c True if the cut cells are cells of the level and not blocked, otherwise @c False.
        """
        affected: frozenset[Cell] = self.cells_of((cut,))
        return affected <= cells and not (affected & blocked_cells)

    def _swap(
        self, ring: ModuleRing, outline: OutlineRing, cut: CornerCut, with_window: bool
    ) -> ModuleRing | None:
        """Replaces the corner of a ring by a diagonal wall.

        Args:
            ring is the ring to edit.
            outline is the outline of the ring.
            cut is the cut.
            with_window is whether the diagonal wall gets a window, if the atlas has one.

        Returns:
            The ring with the corner cut, @c None if the walls at the corner do not add up to exactly the legs
            of the cut, if one of them is a door or a curved wall, or the atlas has no post.
        """
        posts: list[PostModule] = [
            module for module in self._atlas.modules_of(PostModule) if type(module) is PostModule
        ]
        if not posts:
            return None
        leg_u, leg_v = self._legs(cut.rotation)
        removed: list[ModulePlacement] = []
        refilled: list[ModulePlacement] = []
        for leg in (leg_u, leg_v):
            found = self._walls_on_leg(ring, cut, leg)
            if found is None:
                return None
            walls, reached = found
            if reached > cut.size + TOLERANCE:
                # a wide wall reaches past the cut, plain walls take over the rest
                more: list[ModulePlacement] | None = self._refill(cut, leg, cut.size, reached, walls[-1])
                if more is None:
                    return None
                refilled.extend(more)
            removed.extend(walls)
        template = removed[0].module

        corner_post: list[ModulePlacement] = [
            placement
            for placement in ring.placements
            if isinstance(placement.module, PostModule)
            and math.dist(placement.position, cut.point) <= TOLERANCE
        ]
        middle_posts: list[ModulePlacement] = [
            placement
            for placement in ring.placements
            if isinstance(placement.module, PostModule)
            and any(self._on_leg(placement.position, cut, leg, strictly_inside=True) for leg in (leg_u, leg_v))
        ]
        # a post that stood in the middle of a wall that was replaced would stand inside the new walls

        kept: list[ModulePlacement] = [
            placement
            for placement in ring.placements
            if placement not in removed and placement not in corner_post and placement not in middle_posts
        ]
        kept.extend(refilled)

        ends: list[Point] = [
            (cut.point[0] + cut.size * leg[0], cut.point[1] + cut.size * leg[1]) for leg in (leg_u, leg_v)
        ]
        for end in ends:
            if not any(
                isinstance(placement.module, PostModule) and math.dist(placement.position, end) <= TOLERANCE
                for placement in kept
            ):
                kept.append(ModulePlacement(posts[0], end, 0, removed[0].elevation))

        width: float = cut.size * math.sqrt(2.0)
        diagonal: DiagonalWallModule = DiagonalWallModule(width=width, height=template.height, depth=template.depth)
        windows: list[WindowModule] = [
            module for module in self._atlas.modules_of(WindowModule) if isinstance(module, WindowModule)
        ]
        if with_window and windows:
            diagonal = DiagonalWindowModule(
                width=width,
                height=template.height,
                depth=template.depth,
                opening_width=min(windows[-1].opening_width, width * 0.55),
                opening_height=windows[-1].opening_height,
                sill_height=windows[-1].sill_height,
            )
        middle: Point = ((ends[0][0] + ends[1][0]) * 0.5, (ends[0][1] + ends[1][1]) * 0.5)
        kept.append(ModulePlacement(diagonal, middle, cut.rotation, removed[0].elevation))
        return ModuleRing(tuple(kept))

    def _walls_on_leg(
        self, ring: ModuleRing, cut: CornerCut, leg: tuple[int, int]
    ) -> tuple[list[ModulePlacement], float] | None:
        """Collects the walls along one leg of the cut, from the corner until they cover it.

        Args:
            ring is the ring to search.
            cut is the cut.
            leg is the direction from the corner along the wall.

        Returns:
            The walls from the corner and how far they reach in m, which is at least the leg, @c None if
            a gap is left, one of them is a door or a curved wall, or the last one is not a whole number of meters.
        """
        on_leg: list[tuple[float, ModulePlacement]] = []
        for placement in ring.placements:
            if not isinstance(placement.module, (WallModule, WindowModule, DoorModule)):
                continue
            offset_x: float = placement.position[0] - cut.point[0]
            offset_y: float = placement.position[1] - cut.point[1]
            along: float = offset_x * leg[0] + offset_y * leg[1]
            across: float = abs(offset_x * leg[1] - offset_y * leg[0])
            if across <= TOLERANCE and along > 0.0:
                on_leg.append((along, placement))
        on_leg.sort(key=lambda item: item[0])

        walls: list[ModulePlacement] = []
        reached: float = 0.0
        for along, placement in on_leg:
            if reached >= cut.size - TOLERANCE:
                break
            if abs(along - placement.module.width * 0.5 - reached) > TOLERANCE:
                return None
            if isinstance(placement.module, (DoorModule, ArcWallModule, DiagonalWallModule)):
                return None
            walls.append(placement)
            reached += placement.module.width
        if reached < cut.size - TOLERANCE or abs(reached - round(reached)) > TOLERANCE:
            return None
        return walls, reached

    def _refill(
        self, cut: CornerCut, leg: tuple[int, int], start: float, end: float, template: ModulePlacement
    ) -> list[ModulePlacement] | None:
        """Fills the rest of a leg that a wider wall covered with plain walls.

        Args:
            cut is the cut.
            leg is the direction from the corner along the wall.
            start is the distance from the corner where the new walls begin in m.
            end is the distance from the corner where they end in m.
            template is the wall that was replaced, it gives rotation and elevation.

        Returns:
            Plain walls from start to end, widest first, @c None if the atlas lacks walls to fill it exactly.
        """
        widths: list[WallModule] = [
            module for module in self._atlas.modules_of(WallModule) if type(module) is WallModule
        ]
        placements: list[ModulePlacement] = []
        position: float = start
        while end - position > TOLERANCE:
            fitting: list[WallModule] = [module for module in widths if module.width <= end - position + TOLERANCE]
            if not fitting:
                return None
            wall: WallModule = fitting[0]
            center: float = position + wall.width * 0.5
            placements.append(
                replace(
                    template,
                    module=wall,
                    position=(cut.point[0] + leg[0] * center, cut.point[1] + leg[1] * center),
                )
            )
            position += wall.width
        return placements

    @staticmethod
    def _on_leg(position: Point, cut: CornerCut, leg: tuple[int, int], strictly_inside: bool) -> bool:
        """Tests whether a point lies on a leg of the cut.

        Args:
            position is the point in m.
            cut is the cut.
            leg is the direction from the corner along the wall.
            strictly_inside is whether the corner and the end of the leg do not count.

        Returns:
            @c True if the point is on the leg, otherwise @c False.
        """
        offset_x: float = position[0] - cut.point[0]
        offset_y: float = position[1] - cut.point[1]
        along: float = offset_x * leg[0] + offset_y * leg[1]
        across: float = abs(offset_x * leg[1] - offset_y * leg[0])
        margin: float = TOLERANCE if strictly_inside else -TOLERANCE
        return across <= TOLERANCE and margin < along < cut.size - margin
