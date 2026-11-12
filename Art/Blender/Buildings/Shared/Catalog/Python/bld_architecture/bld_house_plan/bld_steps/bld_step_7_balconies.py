# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 7: rings with stairs -> balconies that replace the stairs in front of some doors."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import math
import random

from bld_modules import TOLERANCE, DoorModule, StairModule

from ...bld_create_info import BalconyCreateInfo
from ..bld_house_plan import BalconyPlan, FoundationPlan, ModulePlacement, ModuleRing
from .bld_step_1_footprint import Footprint, Side
from .bld_step_2_outline import OutlineRing, OutlineSegment
from .bld_step_6_stairs import Rectangle, StairPlacer

Cell = tuple[int, int]

# outward side and unit direction per quarter turn, the module front (-Y) turned counter-clockwise
_OUTWARD_SIDES: tuple[Side, ...] = (Side.SOUTH, Side.EAST, Side.NORTH, Side.WEST)
_OUTWARD: tuple[tuple[int, int], ...] = ((0, -1), (1, 0), (0, 1), (-1, 0))


class BalconyPlanner:
    """Gives some doors a balcony on free grid cells in place of their stairs."""

    def plan(
        self,
        rings: tuple[ModuleRing, ...],
        outlines: tuple[OutlineRing, ...],
        footprint: Footprint,
        foundation: FoundationPlan | None,
        create_info: BalconyCreateInfo,
        random_source: random.Random,
    ) -> tuple[tuple[ModuleRing, ...], tuple[BalconyPlan, ...]]:
        """Plans the balconies of one building.

        Args:
            rings are the rings with stairs in front of the doors.
            outlines are the outline rings of the footprint, a balcony never reaches past its wall.
            footprint is the footprint, balconies never cover its cells.
            foundation is the foundation the balconies stand at, None means no balconies.
            create_info is the rules for the balconies.
            random_source is the random stream for the balconies, separate from all other steps.

        Returns:
            The rings without the stairs of balcony doors, and the balconies in door order.
            Doors close together on one wall share one balcony. A balcony shrinks until it fits,
            doors where not even the smallest one fits keep their stairs.
        """
        if foundation is None or not create_info.enabled:
            return rings, ()

        built_cells: frozenset[Cell] = footprint.main_cells.union(*footprint.extension_cells)
        balcony_cells: set[Cell] = set()
        balconies: list[BalconyPlan] = []
        replaced_stairs: set[ModulePlacement] = set()

        for group, segment in self._door_groups(rings, outlines, create_info.merge_door_gap):
            # every roll is taken for every group, so one group never moves the balconies of others
            wanted: bool = random_source.random() < create_info.chance
            depth: int = random_source.randint(create_info.min_depth, create_info.max_depth)
            extra_before: int = random_source.randint(0, create_info.max_extra_width)
            extra_after: int = random_source.randint(0, create_info.max_extra_width)
            if not wanted:
                continue

            own_stairs: list[ModulePlacement] = [
                stair
                for stair in (self._stair_of(door, rings) for door in group)
                if stair is not None
            ]
            foreign_stairs: list[Rectangle] = [
                StairPlacer.rectangle_of(stair, stair.module.width, stair.module.depth)
                for other_ring in rings
                for stair in other_ring.placements
                if isinstance(stair.module, StairModule) and stair not in own_stairs
            ]
            cells: frozenset[Cell] | None = self._fit_cells(
                group,
                segment,
                depth,
                extra_before,
                extra_after,
                create_info.min_depth,
                built_cells,
                balcony_cells,
                foreign_stairs,
            )
            if cells is None:
                continue
            balcony_cells |= cells
            balconies.append(
                BalconyPlan(cells, tuple(group), _OUTWARD_SIDES[group[0].rotation_steps % 4])
            )
            replaced_stairs.update(own_stairs)

        stripped_rings: tuple[ModuleRing, ...] = tuple(
            ModuleRing(tuple(p for p in ring.placements if p not in replaced_stairs))
            for ring in rings
        )
        return stripped_rings, tuple(balconies)

    def _door_groups(
        self,
        rings: tuple[ModuleRing, ...],
        outlines: tuple[OutlineRing, ...],
        merge_gap: float,
    ) -> list[tuple[list[ModulePlacement], OutlineSegment]]:
        """Groups the doors that stand close together on one wall.

        Args:
            rings are the rings with the doors.
            outlines are the outline rings that provide the walls.
            merge_gap is the largest stretch of wall in m between two doors of one group.

        Returns:
            One entry per group with its doors sorted along the wall and the wall they stand on.
            Doors without a wall in the outline are left out.
        """
        doors_per_segment: dict[tuple[int, int], list[ModulePlacement]] = {}
        segments: dict[tuple[int, int], OutlineSegment] = {}
        for ring in rings:
            for door in ring.placements:
                if not isinstance(door.module, DoorModule):
                    continue
                key: tuple[int, int] | None = self._segment_key_of(door, outlines)
                if key is None:
                    continue
                doors_per_segment.setdefault(key, []).append(door)
                segments[key] = outlines[key[0]].segments[key[1]]

        groups: list[tuple[list[ModulePlacement], OutlineSegment]] = []
        for key, doors in doors_per_segment.items():
            along_x: bool = _OUTWARD[doors[0].rotation_steps % 4][0] == 0
            doors.sort(key=lambda door: door.position[0] if along_x else door.position[1])
            current: list[ModulePlacement] = [doors[0]]
            for door in doors[1:]:
                previous: ModulePlacement = current[-1]
                distance: float = (
                    abs(door.position[0] - previous.position[0])
                    if along_x
                    else abs(door.position[1] - previous.position[1])
                )
                gap: float = distance - (door.module.width + previous.module.width) * 0.5
                if gap <= merge_gap + TOLERANCE:
                    current.append(door)
                else:
                    groups.append((current, segments[key]))
                    current = [door]
            groups.append((current, segments[key]))
        return groups

    @staticmethod
    def _segment_key_of(
        door: ModulePlacement, outlines: tuple[OutlineRing, ...]
    ) -> tuple[int, int] | None:
        """Finds the outline segment a door stands on.

        Args:
            door is the door.
            outlines are the outline rings.

        Returns:
            Ring index and segment index, None if no segment of that side carries the door.
        """
        side: Side = _OUTWARD_SIDES[door.rotation_steps % 4]
        for ring_index, ring in enumerate(outlines):
            for segment_index, segment in enumerate(ring.segments):
                if segment.outward is not side:
                    continue
                along_x: bool = side in (Side.NORTH, Side.SOUTH)
                line: float = segment.start[1] if along_x else segment.start[0]
                door_line: float = door.position[1] if along_x else door.position[0]
                door_along: float = door.position[0] if along_x else door.position[1]
                start_along: int = segment.start[0] if along_x else segment.start[1]
                end_along: int = segment.end[0] if along_x else segment.end[1]
                if (
                    abs(line - door_line) <= TOLERANCE
                    and min(start_along, end_along) - TOLERANCE
                    <= door_along
                    <= max(start_along, end_along) + TOLERANCE
                ):
                    return ring_index, segment_index
        return None

    def _fit_cells(
        self,
        doors: list[ModulePlacement],
        segment: OutlineSegment,
        depth: int,
        extra_before: int,
        extra_after: int,
        min_depth: int,
        built_cells: frozenset[Cell],
        balcony_cells: set[Cell],
        foreign_stairs: list[Rectangle],
    ) -> frozenset[Cell] | None:
        """Shrinks a balcony step by step until its cells are free.

        Args:
            doors are the doors the balcony leads to.
            segment is the wall the doors stand on, the balcony ends with it.
            depth is the wanted depth in cells.
            extra_before is the wanted reach past the first door in cells.
            extra_after is the wanted reach past the last door in cells.
            min_depth is the smallest allowed depth in cells.
            built_cells are the cells of the footprint.
            balcony_cells are the cells of the balconies planned so far.
            foreign_stairs are the areas of the stairs of other doors in m.

        Returns:
            The free cells, None if even the smallest balcony does not fit.
        """
        while True:
            cells: frozenset[Cell] = self._cells_of(doors, segment, depth, extra_before, extra_after)
            if self._is_free(cells, built_cells, balcony_cells, foreign_stairs):
                return cells
            # width first, a deeper balcony in front of the door is worth more than a wide one
            if extra_before > 0 or extra_after > 0:
                extra_before = max(0, extra_before - 1)
                extra_after = max(0, extra_after - 1)
            elif depth > min_depth:
                depth -= 1
            else:
                return None

    @staticmethod
    def _cells_of(
        doors: list[ModulePlacement],
        segment: OutlineSegment,
        depth: int,
        extra_before: int,
        extra_after: int,
    ) -> frozenset[Cell]:
        """Lists the cells of a balcony in front of its doors.

        Args:
            doors are the doors, their wall midline lies on a grid line.
            segment is the wall the doors stand on, the cells never reach past its ends.
            depth is the depth in cells away from the wall.
            extra_before is the reach past the first door in cells.
            extra_after is the reach past the last door in cells.

        Returns:
            Cells outside the wall that cover all doors plus the extra reach, flush with the wall ends.
        """
        direction: tuple[int, int] = _OUTWARD[doors[0].rotation_steps % 4]
        along_x: bool = direction[0] == 0  # wall runs along X when it faces south or north
        centers: list[float] = [door.position[0] if along_x else door.position[1] for door in doors]
        wall_line: int = round(doors[0].position[1] if along_x else doors[0].position[0])
        first_along: int = min(
            math.floor(center - door.module.width * 0.5 + TOLERANCE)
            for center, door in zip(centers, doors)
        )
        last_along: int = max(
            math.ceil(center + door.module.width * 0.5 - TOLERANCE) - 1
            for center, door in zip(centers, doors)
        )
        start_along: int = segment.start[0] if along_x else segment.start[1]
        end_along: int = segment.end[0] if along_x else segment.end[1]
        wall_first: int = min(start_along, end_along)
        wall_last: int = max(start_along, end_along) - 1

        cells: set[Cell] = set()
        for along in range(
            max(first_along - extra_before, wall_first), min(last_along + extra_after, wall_last) + 1
        ):
            for step in range(depth):
                # the cell on the positive side of the wall line starts at it, on the negative side ends at it
                across: int = wall_line + step if direction[0] + direction[1] > 0 else wall_line - 1 - step
                cells.add((along, across) if along_x else (across, along))
        return frozenset(cells)

    @staticmethod
    def _is_free(
        cells: frozenset[Cell],
        built_cells: frozenset[Cell],
        balcony_cells: set[Cell],
        foreign_stairs: list[Rectangle],
    ) -> bool:
        """Tests whether a balcony collides with the building, other balconies or other stairs.

        Args:
            cells are the cells of the balcony.
            built_cells are the cells of the footprint.
            balcony_cells are the cells of the balconies planned so far.
            foreign_stairs are the areas of the stairs of other doors in m.

        Returns:
            True if no cell is built up, no cell touches another balcony and no stair is in the way.
        """
        for cell_x, cell_y in cells:
            if (cell_x, cell_y) in built_cells:
                return False
            # touching balconies would melt into one platform with rails through it
            for neighbor in (
                (cell_x, cell_y),
                (cell_x + 1, cell_y),
                (cell_x - 1, cell_y),
                (cell_x, cell_y + 1),
                (cell_x, cell_y - 1),
            ):
                if neighbor in balcony_cells:
                    return False
            cell_area: Rectangle = (cell_x, cell_y, cell_x + 1.0, cell_y + 1.0)
            if any(StairPlacer.overlaps(cell_area, stair) for stair in foreign_stairs):
                return False
        return True

    @staticmethod
    def _stair_of(door: ModulePlacement, rings: tuple[ModuleRing, ...]) -> ModulePlacement | None:
        """Finds the stair the stair placer put in front of a door.

        Args:
            door is the door.
            rings are the rings with the stairs.

        Returns:
            The stair that stands straight out from the door center, None if the door has none.
        """
        direction: tuple[int, int] = _OUTWARD[door.rotation_steps % 4]
        for ring in rings:
            for placement in ring.placements:
                if (
                    not isinstance(placement.module, StairModule)
                    or placement.rotation_steps % 4 != door.rotation_steps % 4
                ):
                    continue
                offset_x: float = placement.position[0] - door.position[0]
                offset_y: float = placement.position[1] - door.position[1]
                along_wall: float = abs(offset_x if direction[0] == 0 else offset_y)
                away_from_wall: float = offset_x * direction[0] + offset_y * direction[1]
                if along_wall <= TOLERANCE and 0.0 < away_from_wall < 1.0:
                    return placement
        return None
