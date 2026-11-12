# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 9: outline and ground floor -> the levels above it, each one repeats the footprint."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import random
from dataclasses import replace

from ...bld_create_info import LevelsCreateInfo, OpeningCreateInfo
from ..bld_house_plan import LevelPlan, ModulePlacement, ModuleRing
from .bld_step_1_footprint import Footprint
from .bld_step_2_outline import OutlineRing
from .bld_step_4_walls import WallFiller
from .bld_step_5_openings import OpeningPlacer
from .bld_step_8_floor import FloorPlanner
from .bld_step_9_level_stairs import LevelStairPlacer


class LevelPlanner:
    """Stacks levels on top of the ground floor, each with a floor slab layer and its own walls."""

    def __init__(
        self,
        wall_filler: WallFiller,
        opening_placer: OpeningPlacer,
        floor_planner: FloorPlanner,
        stair_placer: LevelStairPlacer,
    ) -> None:
        """Creates a level planner.

        Args:
            wall_filler: Fills the outline rings with posts and walls.
            opening_placer: Swaps walls against windows.
            floor_planner: Lays the floor slabs of a level.
            stair_placer: Puts the interior stair up to a level.

        Returns:
            None.
        """
        self._wall_filler: WallFiller = wall_filler
        self._opening_placer: OpeningPlacer = opening_placer
        self._floor_planner: FloorPlanner = floor_planner
        self._stair_placer: LevelStairPlacer = stair_placer
        return None

    def plan(
        self,
        create_info: LevelsCreateInfo,
        openings: OpeningCreateInfo,
        outlines: tuple[OutlineRing, ...],
        ground_rings: tuple[ModuleRing, ...],
        footprint: Footprint,
        ground_elevation: float,
        wall_height: float,
        seed: int,
    ) -> tuple[LevelPlan, ...]:
        """Plans the levels above the ground floor.

        Args:
            create_info is the rules for the levels.
            openings is the rules for the windows, the levels get windows only for now.
            outlines are the outline rings, every level has the same walls as the ground floor.
            ground_rings are the rings of the ground floor, the interior stairs keep clear of them.
            footprint is the footprint, its cells get floor slabs.
            ground_elevation is the height of the ground floor walls above the ground in m.
            wall_height is the height of one wall in m.
            seed is the seed of the building, every level gets its own random streams from it.

        Returns:
            One plan per level from bottom to top, empty if there are no upper levels or the atlas
            has no floor slab of a whole cell.
        """
        slab_height: float | None = self._floor_planner.slab_height
        if create_info.upper_count == 0 or slab_height is None:
            return ()

        levels: list[LevelPlan] = []
        rise: float = wall_height + slab_height
        lower_floor_top: float = ground_elevation
        blocked_cells: frozenset[tuple[int, int]] = frozenset()
        for level_number in range(1, create_info.upper_count + 1):
            # the slabs lie on top of the walls below, the walls of the level on top of the slabs
            slab_elevation: float = (
                ground_elevation + level_number * wall_height + (level_number - 1) * slab_height
            )
            wall_elevation: float = slab_elevation + slab_height

            # own random streams per level, so levels never move the ground floor of a seed
            stair_random: random.Random = random.Random(f"{seed}:level{level_number}:stairs")
            placed: tuple[ModulePlacement, frozenset[tuple[int, int]]] | None = self._stair_placer.place(
                footprint, ground_rings, blocked_cells, lower_floor_top, rise, stair_random
            )
            stairs: tuple[ModulePlacement, ...] = () if placed is None else (placed[0],)
            hole: frozenset[tuple[int, int]] = frozenset() if placed is None else placed[1]

            rings: list[ModuleRing] = []
            if create_info.build_walls:
                wall_random: random.Random = random.Random(f"{seed}:level{level_number}:walls")
                opening_random: random.Random = random.Random(f"{seed}:level{level_number}:openings")
                for outline in outlines:
                    filled: ModuleRing = self._wall_filler.fill(outline, wall_random)
                    with_windows: ModuleRing = self._opening_placer.place(
                        filled, 0, openings, opening_random
                    )
                    rings.append(
                        ModuleRing(
                            tuple(
                                replace(placement, elevation=wall_elevation)
                                for placement in with_windows.placements
                            )
                        )
                    )
            levels.append(
                LevelPlan(
                    elevation=wall_elevation,
                    rings=tuple(rings),
                    floor=self._floor_planner.lay(footprint, slab_elevation, hole),
                    stairs=stairs,
                    hole=hole,
                )
            )
            # the stair to the next level starts on this floor and must not stand on this hole
            lower_floor_top = wall_elevation
            blocked_cells = hole
        return tuple(levels)
