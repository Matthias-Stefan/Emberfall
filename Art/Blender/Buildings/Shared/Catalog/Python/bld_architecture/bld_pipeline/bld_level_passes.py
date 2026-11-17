# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Passes of the levels above the ground floor and the pass that stacks the levels."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import random
from dataclasses import replace

from ..bld_house_plan import Footprint, LevelPlan, ModulePlacement, ModuleRing
from ..bld_planners.bld_apsis_placer import ApsisPlacer
from ..bld_planners.bld_bay_placer import BayPlacer
from ..bld_planners.bld_bracket_placer import BracketPlacer
from ..bld_planners.bld_chamfer_placer import ChamferPlacer
from ..bld_planners.bld_floor_planner import FloorPlanner
from ..bld_planners.bld_level_balcony_placer import LevelBalconyPlacer
from ..bld_planners.bld_level_footprint_designer import LevelFootprintDesigner
from ..bld_planners.bld_level_stair_placer import LevelStairPlacer, StairCandidate
from ..bld_planners.bld_opening_placer import OpeningPlacer
from ..bld_planners.bld_outline_reader import OutlineReader
from ..bld_planners.bld_wall_filler import WallFiller
from .bld_drafts import HouseDraft, LevelDraft
from .bld_plan_pass import HousePass, LevelPass

Cell = tuple[int, int]


class LevelWallPass(LevelPass):
    """Fills every outline of the level with posts, walls and windows, the levels get no doors."""

    def __init__(self, wall_filler: WallFiller, opening_placer: OpeningPlacer) -> None:
        """Creates the pass.

        Args:
            wall_filler is the planner that splits the outline into posts and walls.
            opening_placer is the planner that swaps walls against windows.

        Returns:
            None.
        """
        self._wall_filler: WallFiller = wall_filler
        self._opening_placer: OpeningPlacer = opening_placer
        return None

    def apply(self, draft: LevelDraft) -> None:
        wall_random: random.Random = draft.random("walls")
        opening_random: random.Random = draft.random("openings")
        rings: list[ModuleRing] = []
        for outline in draft.outlines:
            filled: ModuleRing = self._wall_filler.fill(outline, wall_random)
            with_windows: ModuleRing = self._opening_placer.place(
                filled, 0, draft.house.info.openings, opening_random
            )
            rings.append(
                ModuleRing(
                    tuple(
                        replace(placement, elevation=draft.wall_elevation)
                        for placement in with_windows.placements
                    )
                )
            )
        draft.rings = tuple(rings)
        return None


class LevelApsisPass(LevelPass):
    """Carries the round ends of the level below up."""

    def __init__(self, apsis_placer: ApsisPlacer) -> None:
        """Creates the pass.

        Args:
            apsis_placer is the planner of the round ends.

        Returns:
            None.
        """
        self._apsis_placer: ApsisPlacer = apsis_placer
        return None

    def apply(self, draft: LevelDraft) -> None:
        rings: list[ModuleRing] = []
        for ring, outline in zip(draft.rings, draft.outlines):
            ring, round_floor = self._apsis_placer.continue_up(
                ring,
                outline,
                draft.lower_rings,
                draft.wall_elevation,
                draft.slab_elevation,
                draft.slab_height,
            )
            rings.append(ring)
            draft.floor = (*draft.floor, *round_floor)
        draft.rings = tuple(rings)
        return None


class LevelChamferPass(LevelPass):
    """Carries the cut corners of the level below up, never over the stair."""

    def __init__(self, chamfer_placer: ChamferPlacer) -> None:
        """Creates the pass.

        Args:
            chamfer_placer is the planner of the cut corners.

        Returns:
            None.
        """
        self._chamfer_placer: ChamferPlacer = chamfer_placer
        return None

    def apply(self, draft: LevelDraft) -> None:
        stair_cells: frozenset[Cell] = draft.stair.covered | {draft.stair.landing} | draft.hole
        rings: list[ModuleRing] = []
        for ring, outline in zip(draft.rings, draft.outlines):
            ring, cuts = self._chamfer_placer.continue_up(
                ring,
                outline,
                draft.lower_rings,
                draft.footprint.cells,
                stair_cells,
                # a fresh stream per outline, as the planner has always been called
                draft.random("chamfers"),
            )
            rings.append(ring)
            draft.cuts = (*draft.cuts, *cuts)
        draft.rings = tuple(rings)
        return None


class LevelBayPass(LevelPass):
    """Swaps walls of the level against bays that stick out over the level below."""

    def __init__(self, bay_placer: BayPlacer) -> None:
        """Creates the pass.

        Args:
            bay_placer is the planner of the bays.

        Returns:
            None.
        """
        self._bay_placer: BayPlacer = bay_placer
        return None

    def apply(self, draft: LevelDraft) -> None:
        bay_random: random.Random = draft.random("bays")
        rings: list[ModuleRing] = []
        for ring, outline in zip(draft.rings, draft.outlines):
            ring, strips = self._bay_placer.place(
                ring, outline, draft.slab_elevation, draft.house.info.levels, bay_random
            )
            rings.append(ring)
            draft.floor = (*draft.floor, *strips)
        draft.rings = tuple(rings)
        return None


class LevelBracketPass(LevelPass):
    """Puts braces under the bays where a wall of the level below carries them."""

    def __init__(self, bracket_placer: BracketPlacer) -> None:
        """Creates the pass.

        Args:
            bracket_placer is the planner of the braces.

        Returns:
            None.
        """
        self._bracket_placer: BracketPlacer = bracket_placer
        return None

    def apply(self, draft: LevelDraft) -> None:
        for ring in draft.rings:
            draft.floor = (
                *draft.floor,
                *self._bracket_placer.place(ring, draft.lower_rings, draft.slab_elevation),
            )
        return None


class LevelBalconyPass(LevelPass):
    """Builds a balcony on pillars in front of a new door, on the first level only."""

    def __init__(self, balcony_placer: LevelBalconyPlacer) -> None:
        """Creates the pass.

        Args:
            balcony_placer is the planner of the balconies on pillars.

        Returns:
            None.
        """
        self._balcony_placer: LevelBalconyPlacer = balcony_placer
        return None

    def apply(self, draft: LevelDraft) -> None:
        # the pillars of a higher balcony would have to pass the balcony of the level below
        if draft.number != 1 or not draft.outlines:
            return None
        rings, rail_ring, slabs = self._balcony_placer.place(
            draft.rings,
            draft.outlines,
            draft.footprint.cells,
            draft.lower_footprint.cells,
            draft.house.ground_obstacles(),
            draft.slab_elevation,
            draft.wall_elevation,
            draft.house.info.levels,
            draft.random("balconies"),
        )
        draft.rings = rings if rail_ring is None else (*rings, rail_ring)
        draft.floor = (*draft.floor, *slabs)
        return None


class LevelFloorPass(LevelPass):
    """Lays the floor slabs of the level without the stair hole and the cut corners."""

    def __init__(self, floor_planner: FloorPlanner, chamfer_placer: ChamferPlacer) -> None:
        """Creates the pass.

        Args:
            floor_planner is the planner of the slabs.
            chamfer_placer takes the cut corners out of the slabs.

        Returns:
            None.
        """
        self._floor_planner: FloorPlanner = floor_planner
        self._chamfer_placer: ChamferPlacer = chamfer_placer
        return None

    def apply(self, draft: LevelDraft) -> None:
        slabs = self._floor_planner.lay(draft.footprint, draft.slab_elevation, draft.hole)
        draft.floor = (*self._chamfer_placer.cut_floor(slabs, draft.cuts), *draft.floor)
        return None


class LevelsPass(HousePass):
    """Stacks levels on the ground floor, picks footprint and stair of each and runs the level passes on it."""

    def __init__(
        self,
        outline_reader: OutlineReader,
        footprint_designer: LevelFootprintDesigner,
        stair_placer: LevelStairPlacer,
        floor_planner: FloorPlanner,
        level_passes: tuple[LevelPass, ...],
    ) -> None:
        """Creates the pass.

        Args:
            outline_reader reads the outline rings of a level footprint.
            footprint_designer cuts the footprints of the levels out of the footprint below.
            stair_placer finds the interior stairs up to a level.
            floor_planner knows the slab height.
            level_passes are the passes run on every level, in order.

        Returns:
            None.
        """
        self._outline_reader: OutlineReader = outline_reader
        self._footprint_designer: LevelFootprintDesigner = footprint_designer
        self._stair_placer: LevelStairPlacer = stair_placer
        self._floor_planner: FloorPlanner = floor_planner
        self._level_passes: tuple[LevelPass, ...] = level_passes
        return None

    def apply(self, draft: HouseDraft) -> None:
        levels_info = draft.info.levels
        slab_height: float | None = self._floor_planner.slab_height
        if levels_info.upper_count == 0 or slab_height is None:
            return None

        wall_height: float = draft.style.wall_height
        rise: float = wall_height + slab_height
        lower_footprint: Footprint = draft.footprint
        lower_rings: tuple[ModuleRing, ...] = draft.rings
        lower_floor_top: float = draft.elevation
        # a stair must not stand in a corner that is cut off
        blocked_cells: frozenset[Cell] = ChamferPlacer.cells_of(ChamferPlacer.cuts_of(draft.rings))
        levels: list[LevelPlan] = []
        for number in range(1, levels_info.upper_count + 1):
            # one stream for the candidates and the pick, so the pick depends on the candidates only
            stair_random: random.Random = draft.random(f"level{number}:stairs")
            candidates: tuple[StairCandidate, ...] = self._stair_placer.candidates(
                lower_footprint.cells, lower_rings, blocked_cells, lower_floor_top, rise, stair_random
            )
            chosen: tuple[Footprint, StairCandidate] | None = self._choose(
                draft, lower_footprint, candidates, draft.random(f"level{number}:footprint"), stair_random
            )
            if chosen is None:
                break  # nothing leads up here, a level nobody can reach is not built
            footprint, stair = chosen

            # the slabs lie on top of the walls below, the walls of the level on top of the slabs
            level: LevelDraft = LevelDraft(
                house=draft,
                number=number,
                footprint=footprint,
                outlines=self._outline_reader.read(footprint) if levels_info.build_walls else (),
                stair=stair,
                lower_footprint=lower_footprint,
                lower_rings=lower_rings,
                slab_elevation=draft.elevation + number * wall_height + (number - 1) * slab_height,
                slab_height=slab_height,
            )
            for level_pass in self._level_passes:
                level_pass.apply(level)
            levels.append(level.to_plan())

            # the stair to the next level starts on this floor and must not stand on this hole
            lower_footprint = footprint
            lower_rings = level.rings
            lower_floor_top = level.wall_elevation
            blocked_cells = level.hole | ChamferPlacer.cells_of(level.cuts)
        draft.levels = tuple(levels)
        return None

    def _choose(
        self,
        draft: HouseDraft,
        lower_footprint: Footprint,
        candidates: tuple[StairCandidate, ...],
        footprint_random: random.Random,
        stair_random: random.Random,
    ) -> tuple[Footprint, StairCandidate] | None:
        """Picks the footprint of a level together with the stair that leads up to it.

        A new footprint is only taken if one stair lands on it. If none of the rolled footprints
        works, the level repeats the footprint of the level below.

        Args:
            draft is the house the level is stacked on.
            lower_footprint is the footprint of the level below.
            candidates are the stairs that fit on the level below.
            footprint_random is the random stream that rolls the footprints.
            stair_random is the random stream that picks the stair.

        Returns:
            The footprint and its stair, @c None if not even the footprint of the level below can be reached.
        """
        levels_info = draft.info.levels
        for option in self._footprint_designer.options(levels_info, lower_footprint, footprint_random):
            usable: list[StairCandidate] = self._landing_on(candidates, option.cells, levels_info.build_walls)
            if usable:
                return option, stair_random.choice(usable)
        usable = self._landing_on(candidates, lower_footprint.cells, levels_info.build_walls)
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
            The candidates that land on one of the cells, with @c keep_off_walls only those whose
            hole has no cell at the outline of the level above.
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
