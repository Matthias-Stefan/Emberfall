# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Designs building plans from create infos."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import random
from dataclasses import replace

from bld_modules import DoorModule

from .bld_create_info import BuildingCreateInfo
from .bld_house_plan import (
    BalconyPlanner,
    Footprint,
    FloorPlanner,
    FootprintDesigner,
    FoundationPlan,
    FoundationPlanner,
    HousePlan,
    ApsisPlacer,
    ChamferPlacer,
    BayPlacer,
    BracketPlacer,
    LevelBalconyPlacer,
    LevelFootprintDesigner,
    LevelPlanner,
    LevelStairPlacer,
    ModuleRing,
    OpeningPlacer,
    OutlineReader,
    OutlineRing,
    StairPlacer,
    WallFiller,
)
from .bld_style import Style


class Architect:
    """Designs building plans in nine steps: footprint, outline, foundation, walls, openings, stairs, balconies, floor, levels."""

    def __init__(self, style: Style) -> None:
        """Creates an architect.

        Args:
            style: Look of the buildings, provides the modules the architect may plan with.

        Returns:
            None.
        """
        self._style: Style = style
        self._footprint_designer: FootprintDesigner = FootprintDesigner()
        self._outline_reader: OutlineReader = OutlineReader()
        self._wall_filler: WallFiller = WallFiller(style.atlas)
        self._opening_placer: OpeningPlacer = OpeningPlacer(style.atlas)
        self._foundation_planner: FoundationPlanner = FoundationPlanner()
        self._stair_placer: StairPlacer = StairPlacer(style.atlas)
        self._balcony_planner: BalconyPlanner = BalconyPlanner(style.atlas)
        self._floor_planner: FloorPlanner = FloorPlanner(style.atlas)
        self._apsis_placer: ApsisPlacer = ApsisPlacer(style.atlas)
        self._chamfer_placer: ChamferPlacer = ChamferPlacer(style.atlas)
        self._level_planner: LevelPlanner = LevelPlanner(
            self._outline_reader,
            self._wall_filler,
            self._opening_placer,
            self._floor_planner,
            LevelFootprintDesigner(),
            self._apsis_placer,
            self._chamfer_placer,
            BayPlacer(style.atlas),
            BracketPlacer(style.atlas),
            LevelBalconyPlacer(style.atlas, self._floor_planner),
            LevelStairPlacer(style.atlas),
        )

    def design(self, create_info: BuildingCreateInfo) -> HousePlan:
        """Designs one building.

        Args:
            create_info: Description of the building to design.

        Returns:
            Footprint and module rings of the building, carrying the seed it was designed with.
        """
        footprint: Footprint = self._footprint_designer.design(create_info)

        outlines: tuple[OutlineRing, ...] = self._outline_reader.read(footprint)

        # planned early, the doors need to know the foundation to leave room for their stairs
        foundation: FoundationPlan | None = self._foundation_planner.plan(
            outlines, create_info.foundation, self._style.wall_depth
        )

        # own random stream, so changes to the walls never move the footprint of a seed
        wall_random: random.Random = random.Random(f"{create_info.seed}:walls")
        filled_rings: tuple[ModuleRing, ...] = tuple(
            self._wall_filler.fill(ring, wall_random) for ring in outlines
        )

        # own random stream again, so openings never move the walls of a seed
        opening_random: random.Random = random.Random(f"{create_info.seed}:openings")
        remaining_doors: int = create_info.openings.door_count
        rings: list[ModuleRing] = []
        for filled_ring in filled_rings:
            ring_with_openings: ModuleRing = self._opening_placer.place(
                filled_ring,
                remaining_doors,
                create_info.openings,
                opening_random,
                lambda wall: self._stair_placer.has_room(wall, filled_rings, foundation),
            )
            remaining_doors -= sum(
                isinstance(placement.module, DoorModule)
                for placement in ring_with_openings.placements
            )
            rings.append(ring_with_openings)

        lifted_rings: tuple[ModuleRing, ...] = tuple(
            self._foundation_planner.lift(ring, foundation) for ring in rings
        )

        # own random stream again, so the stair variants never move walls or openings
        stair_random: random.Random = random.Random(f"{create_info.seed}:stairs")
        stair_rings: tuple[ModuleRing, ...] = self._stair_placer.place(
            lifted_rings, foundation, stair_random
        )

        # own random stream again, balconies only replace stairs, they never move walls or openings
        balcony_random: random.Random = random.Random(f"{create_info.seed}:balconies")
        balcony_rings, balconies = self._balcony_planner.plan(
            stair_rings, outlines, footprint, foundation, create_info.balconies, balcony_random
        )

        # own random stream again, the round end only turns a free wall, so it comes last
        round_rings, round_base = self._apsis_placer.place_ground(
            balcony_rings,
            outlines,
            footprint,
            foundation,
            LevelPlanner.ground_obstacles(balcony_rings, balconies),
            create_info.levels,
            random.Random(f"{create_info.seed}:apsis"),
        )

        # cut corners come after the round end, they keep away from the walls it replaced
        cut_rings, cuts = self._chamfer_placer.place_ground(
            round_rings,
            outlines,
            footprint,
            create_info.levels,
            random.Random(f"{create_info.seed}:chamfers"),
        )
        balcony_rings = cut_rings
        if foundation is not None:
            foundation = replace(foundation, cuts=cuts)
        return HousePlan(
            footprint=footprint,
            rings=balcony_rings,
            balconies=balconies,
            foundation=foundation,
            floor=(*self._chamfer_placer.cut_floor(self._floor_planner.plan(footprint, foundation), cuts), *round_base),
            levels=self._level_planner.plan(
                create_info,
                balcony_rings,
                balconies,
                footprint,
                foundation.height if foundation is not None else 0.0,
                self._style.wall_height,
            ),
        )
