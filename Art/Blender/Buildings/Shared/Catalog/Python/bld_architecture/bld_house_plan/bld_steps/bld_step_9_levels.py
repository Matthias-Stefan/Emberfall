# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 9: ground floor -> the levels above it, each with a footprint of its own and a stair up to it."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import random
from dataclasses import replace

from ...bld_create_info import BuildingCreateInfo
from bld_modules import ArcWallModule, StairModule

from ..bld_house_plan import BalconyPlan, CornerCut, LevelPlan, ModulePlacement, ModuleRing
from .bld_step_1_footprint import Footprint
from .bld_step_2_outline import OutlineReader, OutlineRing
from .bld_step_4_walls import WallFiller
from .bld_step_5_openings import OpeningPlacer
from .bld_step_6_stairs import Rectangle, StairPlacer
from .bld_step_8_floor import FloorPlanner
from .bld_step_9_apsis import ApsisPlacer
from .bld_step_9_bays import BayPlacer
from .bld_step_9_chamfers import ChamferPlacer
from .bld_step_9_brackets import BracketPlacer
from .bld_step_9_level_balconies import LevelBalconyPlacer
from .bld_step_9_level_footprints import LevelFootprintDesigner
from .bld_step_9_level_stairs import LevelStairPlacer, StairCandidate

Cell = tuple[int, int]


class LevelPlanner:
    """Stacks levels on top of the ground floor, each with a footprint of its own, a floor slab layer and a stair."""

    def __init__(
        self,
        outline_reader: OutlineReader,
        wall_filler: WallFiller,
        opening_placer: OpeningPlacer,
        floor_planner: FloorPlanner,
        footprint_designer: LevelFootprintDesigner,
        apsis_placer: ApsisPlacer,
        chamfer_placer: ChamferPlacer,
        bay_placer: BayPlacer,
        bracket_placer: BracketPlacer,
        balcony_placer: LevelBalconyPlacer,
        stair_placer: LevelStairPlacer,
    ) -> None:
        """Creates a level planner.

        Args:
            outline_reader: Reads the outline rings of a level footprint.
            wall_filler: Fills the outline rings with posts and walls.
            opening_placer: Swaps walls against windows.
            floor_planner: Lays the floor slabs of a level.
            footprint_designer: Cuts the footprints of the levels out of the footprint below.
            apsis_placer: Carries the round ends of the level below up.
            chamfer_placer: Carries the cut corners of the level below up.
            bay_placer: Swaps walls of the levels against bays.
            bracket_placer: Puts braces under the bays.
            balcony_placer: Builds balconies on pillars in front of new doors.
            stair_placer: Finds the interior stairs up to a level.

        Returns:
            None.
        """
        self._outline_reader: OutlineReader = outline_reader
        self._wall_filler: WallFiller = wall_filler
        self._opening_placer: OpeningPlacer = opening_placer
        self._floor_planner: FloorPlanner = floor_planner
        self._footprint_designer: LevelFootprintDesigner = footprint_designer
        self._apsis_placer: ApsisPlacer = apsis_placer
        self._chamfer_placer: ChamferPlacer = chamfer_placer
        self._bay_placer: BayPlacer = bay_placer
        self._bracket_placer: BracketPlacer = bracket_placer
        self._balcony_placer: LevelBalconyPlacer = balcony_placer
        self._stair_placer: LevelStairPlacer = stair_placer
        return None

    def plan(
        self,
        building_info: BuildingCreateInfo,
        ground_rings: tuple[ModuleRing, ...],
        ground_balconies: tuple[BalconyPlan, ...],
        ground_footprint: Footprint,
        ground_elevation: float,
        wall_height: float,
    ) -> tuple[LevelPlan, ...]:
        """Plans the levels above the ground floor.

        Args:
            building_info is the building, its levels rules and seed decide what is planned.
            ground_rings are the rings of the ground floor, the interior stair keeps clear of them.
            ground_balconies are the balconies of the ground floor, the pillars of the balconies above keep clear of them.
            ground_footprint is the footprint of the ground floor.
            ground_elevation is the height of the ground floor walls above the ground in m.
            wall_height is the height of one wall in m.

        Returns:
            One plan per level from bottom to top, empty if there are no upper levels or the atlas
            has no floor slab of a whole cell. Planning stops below the first level that no stair
            can reach, so every returned level can be walked up to.
        """
        levels_info = building_info.levels
        slab_height: float | None = self._floor_planner.slab_height
        if levels_info.upper_count == 0 or slab_height is None:
            return ()

        levels: list[LevelPlan] = []
        rise: float = wall_height + slab_height
        lower_footprint: Footprint = ground_footprint
        lower_rings: tuple[ModuleRing, ...] = ground_rings
        lower_floor_top: float = ground_elevation
        # a stair must not stand in a corner that is cut off
        blocked_cells: frozenset[Cell] = ChamferPlacer.cells_of(ChamferPlacer.cuts_of(ground_rings))
        for level_number in range(1, levels_info.upper_count + 1):
            # the slabs lie on top of the walls below, the walls of the level on top of the slabs
            slab_elevation: float = (
                ground_elevation + level_number * wall_height + (level_number - 1) * slab_height
            )
            wall_elevation: float = slab_elevation + slab_height

            # own random streams per level, so levels never move the ground floor of a seed
            seed: int = building_info.seed
            stair_random: random.Random = random.Random(f"{seed}:level{level_number}:stairs")
            footprint_random: random.Random = random.Random(f"{seed}:level{level_number}:footprint")
            candidates: tuple[StairCandidate, ...] = self._stair_placer.candidates(
                self._cells_of(lower_footprint),
                lower_rings,
                blocked_cells,
                lower_floor_top,
                rise,
                stair_random,
            )
            chosen: tuple[Footprint, StairCandidate] | None = self._choose(
                building_info, lower_footprint, candidates, footprint_random, stair_random
            )
            if chosen is None:
                break  # nothing leads up here, a level nobody can reach is not built
            footprint, candidate = chosen
            hole: frozenset[Cell] = candidate.covered & self._cells_of(footprint)

            rings: list[ModuleRing] = []
            bay_floor: list[ModulePlacement] = []
            level_cuts: list[CornerCut] = []
            if levels_info.build_walls:
                wall_random: random.Random = random.Random(f"{seed}:level{level_number}:walls")
                opening_random: random.Random = random.Random(f"{seed}:level{level_number}:openings")
                bay_random: random.Random = random.Random(f"{seed}:level{level_number}:bays")
                outlines: tuple[OutlineRing, ...] = self._outline_reader.read(footprint)
                for outline in outlines:
                    ring: ModuleRing = self._ring_of(
                        outline, wall_elevation, building_info, wall_random, opening_random
                    )
                    ring, round_floor = self._apsis_placer.continue_up(
                        ring,
                        outline,
                        lower_rings,
                        wall_elevation,
                        slab_elevation,
                        self._floor_planner.slab_height or 0.0,
                    )
                    bay_floor.extend(round_floor)
                    ring, cuts = self._chamfer_placer.continue_up(
                        ring,
                        outline,
                        lower_rings,
                        self._cells_of(footprint),
                        candidate.covered | {candidate.landing} | hole,
                        random.Random(f"{seed}:level{level_number}:chamfers"),
                    )
                    level_cuts.extend(cuts)
                    ring, strips = self._bay_placer.place(
                        ring, outline, slab_elevation, levels_info, bay_random
                    )
                    rings.append(ring)
                    bay_floor.extend(strips)
                    bay_floor.extend(self._bracket_placer.place(ring, lower_rings, slab_elevation))
                if level_number == 1:
                    # the pillars of a higher balcony would have to pass the balcony of the level below
                    balcony_rings, balcony_extras, balcony_floor = self._balcony_placer.place(
                        tuple(rings),
                        outlines,
                        self._cells_of(footprint),
                        self._cells_of(lower_footprint),
                        self.ground_obstacles(ground_rings, ground_balconies),
                        slab_elevation,
                        wall_elevation,
                        levels_info,
                        random.Random(f"{seed}:level{level_number}:balconies"),
                    )
                    rings = list(balcony_rings)
                    if balcony_extras is not None:
                        rings.append(balcony_extras)
                    bay_floor.extend(balcony_floor)
            levels.append(
                LevelPlan(
                    footprint=footprint,
                    elevation=wall_elevation,
                    rings=tuple(rings),
                    floor=(
                        *self._chamfer_placer.cut_floor(
                            self._floor_planner.lay(footprint, slab_elevation, hole), tuple(level_cuts)
                        ),
                        *bay_floor,
                    ),
                    stairs=(candidate.stair,),
                    hole=hole,
                )
            )
            # the stair to the next level starts on this floor and must not stand on this hole
            lower_footprint = footprint
            lower_rings = tuple(rings)
            lower_floor_top = wall_elevation
            blocked_cells = hole | ChamferPlacer.cells_of(tuple(level_cuts))
        return tuple(levels)

    def _choose(
        self,
        building_info: BuildingCreateInfo,
        lower_footprint: Footprint,
        candidates: tuple[StairCandidate, ...],
        footprint_random: random.Random,
        stair_random: random.Random,
    ) -> tuple[Footprint, StairCandidate] | None:
        """Picks the footprint of a level together with the stair that leads up to it.

        A new footprint is only taken if one stair lands on it. If none of the rolled footprints
        works, the level repeats the footprint of the level below.

        Args:
            building_info is the building the footprint is rolled for.
            lower_footprint is the footprint of the level below.
            candidates are the stairs that fit on the level below.
            footprint_random is the random stream that rolls the footprints.
            stair_random is the random stream that picks the stair.

        Returns:
            The footprint and its stair, None if not even the footprint of the level below can be reached.
        """
        levels_info = building_info.levels
        for option in self._footprint_designer.options(levels_info, lower_footprint, footprint_random):
            usable: list[StairCandidate] = self._landing_on(
                candidates, self._cells_of(option), levels_info.build_walls
            )
            if usable:
                return option, stair_random.choice(usable)
        usable = self._landing_on(candidates, self._cells_of(lower_footprint), levels_info.build_walls)
        return (lower_footprint, stair_random.choice(usable)) if usable else None

    @staticmethod
    def _landing_on(
        candidates: tuple[StairCandidate, ...], cells: frozenset[Cell], keep_off_walls: bool
    ) -> list[StairCandidate]:
        """Filters the stairs whose landing cell has a floor.

        Args:
            candidates are the stairs to filter.
            cells are the cells of the level above.
            keep_off_walls is whether the hole of the stair must lie clear of the walls of the level above.

        Returns:
            The candidates that land on one of the cells. With keep_off_walls only those whose
            hole has no cell at the outline of the level above, the walls would hang over it.
        """
        interior: frozenset[Cell] = frozenset(
            (cell_x, cell_y)
            for cell_x, cell_y in cells
            if all(
                neighbor in cells
                for neighbor in (
                    (cell_x + 1, cell_y), (cell_x - 1, cell_y), (cell_x, cell_y + 1), (cell_x, cell_y - 1)
                )
            )
        )
        return [
            candidate
            for candidate in candidates
            if candidate.landing in cells
            and (not keep_off_walls or (candidate.covered & cells) <= interior)
        ]

    def _ring_of(
        self,
        outline: OutlineRing,
        wall_elevation: float,
        building_info: BuildingCreateInfo,
        wall_random: random.Random,
        opening_random: random.Random,
    ) -> ModuleRing:
        """Builds the walls of one outline of a level.

        Args:
            outline is the outline ring to fill.
            wall_elevation is the height of the wall bottoms in m.
            building_info is the building, its openings rules apply, the levels get windows only for now.
            wall_random is the random stream of the walls.
            opening_random is the random stream of the openings.

        Returns:
            The ring with all placements lifted to the wall elevation.
        """
        filled: ModuleRing = self._wall_filler.fill(outline, wall_random)
        with_windows: ModuleRing = self._opening_placer.place(
            filled, 0, building_info.openings, opening_random
        )
        return ModuleRing(
            tuple(
                replace(placement, elevation=wall_elevation)
                for placement in with_windows.placements
            )
        )

    @staticmethod
    def ground_obstacles(
        ground_rings: tuple[ModuleRing, ...], ground_balconies: tuple[BalconyPlan, ...]
    ) -> tuple[Rectangle, ...]:
        """Collects the areas on the ground that pillars of a balcony must keep clear of.

        Args:
            ground_rings are the rings of the ground floor, their stairs count.
            ground_balconies are the balconies of the ground floor, their blocks and stairs count.

        Returns:
            One area per stair, per balcony cell and per balcony stair.
        """
        obstacles: list[Rectangle] = [
            StairPlacer.rectangle_of(placement, placement.module.width, placement.module.depth)
            for ring in ground_rings
            for placement in ring.placements
            if isinstance(placement.module, StairModule)
        ]
        # the half circles of round ends reach out of the wall line
        obstacles.extend(
            LevelBalconyPlacer.rectangle_of_wall(placement)
            for ring in ground_rings
            for placement in ring.placements
            if isinstance(placement.module, ArcWallModule)
        )
        for balcony in ground_balconies:
            obstacles.extend((cell_x, cell_y, cell_x + 1.0, cell_y + 1.0) for cell_x, cell_y in balcony.cells)
            obstacles.extend(
                StairPlacer.rectangle_of(stair, stair.module.width, stair.module.depth)
                for stair in balcony.stairs
            )
        return tuple(obstacles)

    @staticmethod
    def _cells_of(footprint: Footprint) -> frozenset[Cell]:
        """Collects all cells of a footprint.

        Args:
            footprint is the footprint to read.

        Returns:
            The cells of the main building and all extensions.
        """
        return footprint.main_cells.union(*footprint.extension_cells)
