# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Passes of the ground floor, each one hands the draft to one planner and stores its result."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import random
from dataclasses import replace

from bld_modules import DoorModule

from ..bld_house_plan import ModuleRing
from ..bld_planners.bld_apsis_placer import ApsisPlacer
from ..bld_planners.bld_balcony_planner import BalconyPlanner
from ..bld_planners.bld_chamfer_placer import ChamferPlacer
from ..bld_planners.bld_floor_planner import FloorPlanner
from ..bld_planners.bld_foundation_planner import FoundationPlanner
from ..bld_planners.bld_opening_placer import OpeningPlacer
from ..bld_planners.bld_stair_placer import StairPlacer
from ..bld_planners.bld_wall_filler import WallFiller
from .bld_drafts import HouseDraft
from .bld_plan_pass import HousePass


class FoundationPass(HousePass):
    """Plans the foundation, early because the doors need to know it to leave room for their stairs."""

    def __init__(self, foundation_planner: FoundationPlanner) -> None:
        """Creates the pass.

        Args:
            foundation_planner is the planner of the stone band.

        Returns:
            None.
        """
        self._foundation_planner: FoundationPlanner = foundation_planner
        return None

    def apply(self, draft: HouseDraft) -> None:
        draft.foundation = self._foundation_planner.plan(
            draft.outlines, draft.info.foundation, draft.style.wall_depth
        )
        return None


class WallPass(HousePass):
    """Fills every outline with posts and walls."""

    def __init__(self, wall_filler: WallFiller) -> None:
        """Creates the pass.

        Args:
            wall_filler is the planner that splits the outline into posts and walls.

        Returns:
            None.
        """
        self._wall_filler: WallFiller = wall_filler
        return None

    def apply(self, draft: HouseDraft) -> None:
        wall_random: random.Random = draft.random("walls")
        draft.rings = tuple(self._wall_filler.fill(outline, wall_random) for outline in draft.outlines)
        return None


class OpeningPass(HousePass):
    """Swaps walls against doors and windows, doors only where a stair fits in front of them."""

    def __init__(self, opening_placer: OpeningPlacer, stair_placer: StairPlacer) -> None:
        """Creates the pass.

        Args:
            opening_placer is the planner that swaps the walls.
            stair_placer is asked whether a stair fits in front of a door.

        Returns:
            None.
        """
        self._opening_placer: OpeningPlacer = opening_placer
        self._stair_placer: StairPlacer = stair_placer
        return None

    def apply(self, draft: HouseDraft) -> None:
        opening_random: random.Random = draft.random("openings")
        filled_rings: tuple[ModuleRing, ...] = draft.rings
        remaining_doors: int = draft.info.openings.door_count
        rings: list[ModuleRing] = []
        for filled_ring in filled_rings:
            ring: ModuleRing = self._opening_placer.place(
                filled_ring,
                remaining_doors,
                draft.info.openings,
                opening_random,
                lambda wall: self._stair_placer.has_room(wall, filled_rings, draft.foundation),
            )
            remaining_doors -= sum(isinstance(placement.module, DoorModule) for placement in ring.placements)
            rings.append(ring)
        draft.rings = tuple(rings)
        return None


class LiftPass(HousePass):
    """Lifts all rings onto the foundation."""

    def __init__(self, foundation_planner: FoundationPlanner) -> None:
        """Creates the pass.

        Args:
            foundation_planner is the planner that knows the foundation height.

        Returns:
            None.
        """
        self._foundation_planner: FoundationPlanner = foundation_planner
        return None

    def apply(self, draft: HouseDraft) -> None:
        draft.rings = tuple(self._foundation_planner.lift(ring, draft.foundation) for ring in draft.rings)
        return None


class StairPass(HousePass):
    """Puts a stair in front of every door that stands on a foundation."""

    def __init__(self, stair_placer: StairPlacer) -> None:
        """Creates the pass.

        Args:
            stair_placer is the planner of the stairs.

        Returns:
            None.
        """
        self._stair_placer: StairPlacer = stair_placer
        return None

    def apply(self, draft: HouseDraft) -> None:
        draft.rings = self._stair_placer.place(draft.rings, draft.foundation, draft.random("stairs"))
        return None


class BalconyPass(HousePass):
    """Replaces the stairs in front of some doors by balconies, walls and openings stay."""

    def __init__(self, balcony_planner: BalconyPlanner) -> None:
        """Creates the pass.

        Args:
            balcony_planner is the planner of the balconies.

        Returns:
            None.
        """
        self._balcony_planner: BalconyPlanner = balcony_planner
        return None

    def apply(self, draft: HouseDraft) -> None:
        draft.rings, draft.balconies = self._balcony_planner.plan(
            draft.rings,
            draft.outlines,
            draft.footprint,
            draft.foundation,
            draft.info.balconies,
            draft.random("balconies"),
        )
        return None


class ApsisPass(HousePass):
    """Turns a free wall into a round end, late because it only takes walls nothing else needs."""

    def __init__(self, apsis_placer: ApsisPlacer) -> None:
        """Creates the pass.

        Args:
            apsis_placer is the planner of the round ends.

        Returns:
            None.
        """
        self._apsis_placer: ApsisPlacer = apsis_placer
        return None

    def apply(self, draft: HouseDraft) -> None:
        draft.rings, round_floor = self._apsis_placer.place_ground(
            draft.rings,
            draft.outlines,
            draft.footprint,
            draft.foundation,
            draft.ground_obstacles(),
            draft.info.levels,
            draft.random("apsis"),
        )
        draft.floor = (*draft.floor, *round_floor)
        return None


class ChamferPass(HousePass):
    """Cuts outer corners off, after the round end so the cuts keep away from the walls it replaced."""

    def __init__(self, chamfer_placer: ChamferPlacer) -> None:
        """Creates the pass.

        Args:
            chamfer_placer is the planner of the cut corners.

        Returns:
            None.
        """
        self._chamfer_placer: ChamferPlacer = chamfer_placer
        return None

    def apply(self, draft: HouseDraft) -> None:
        draft.rings, draft.cuts = self._chamfer_placer.place_ground(
            draft.rings, draft.outlines, draft.footprint, draft.info.levels, draft.random("chamfers")
        )
        if draft.foundation is not None:
            draft.foundation = replace(draft.foundation, cuts=draft.cuts)
        return None


class FloorPass(HousePass):
    """Lays the floor slabs of the ground floor without the cut corners."""

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

    def apply(self, draft: HouseDraft) -> None:
        slabs = self._floor_planner.plan(draft.footprint, draft.foundation)
        draft.floor = (*self._chamfer_placer.cut_floor(slabs, draft.cuts), *draft.floor)
        return None
