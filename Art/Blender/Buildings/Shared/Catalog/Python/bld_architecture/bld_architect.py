# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Designs building plans from create infos."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from .bld_create_info import BuildingCreateInfo
from .bld_house_plan import Footprint, HousePlan
from .bld_pipeline import (
    ApsisPass,
    BalconyPass,
    ChamferPass,
    FloorPass,
    FoundationPass,
    HouseDraft,
    HousePass,
    LevelApsisPass,
    LevelBalconyPass,
    LevelBayPass,
    LevelBracketPass,
    LevelChamferPass,
    LevelFloorPass,
    LevelPass,
    LevelsPass,
    LevelWallPass,
    LiftPass,
    OpeningPass,
    StairPass,
    WallPass,
)
from .bld_planners.bld_apsis_placer import ApsisPlacer
from .bld_planners.bld_balcony_planner import BalconyPlanner
from .bld_planners.bld_bay_placer import BayPlacer
from .bld_planners.bld_bracket_placer import BracketPlacer
from .bld_planners.bld_chamfer_placer import ChamferPlacer
from .bld_planners.bld_floor_planner import FloorPlanner
from .bld_planners.bld_footprint_designer import FootprintDesigner
from .bld_planners.bld_foundation_planner import FoundationPlanner
from .bld_planners.bld_level_balcony_placer import LevelBalconyPlacer
from .bld_planners.bld_level_footprint_designer import LevelFootprintDesigner
from .bld_planners.bld_level_stair_placer import LevelStairPlacer
from .bld_planners.bld_opening_placer import OpeningPlacer
from .bld_planners.bld_outline_reader import OutlineReader
from .bld_planners.bld_stair_placer import StairPlacer
from .bld_planners.bld_wall_filler import WallFiller
from .bld_style import Style


class Architect:
    """Designs building plans: rolls the footprint, then runs the passes in the order listed here."""

    def __init__(self, style: Style) -> None:
        """Creates an architect and wires up its passes.

        Args:
            style is the look of the buildings, it provides the modules the architect may plan with.

        Returns:
            None.
        """
        atlas = style.atlas
        self._style: Style = style
        self._footprint_designer: FootprintDesigner = FootprintDesigner()
        self._outline_reader: OutlineReader = OutlineReader()

        # planners used by several passes
        foundation_planner: FoundationPlanner = FoundationPlanner()
        wall_filler: WallFiller = WallFiller(atlas)
        opening_placer: OpeningPlacer = OpeningPlacer(atlas)
        stair_placer: StairPlacer = StairPlacer(atlas)
        floor_planner: FloorPlanner = FloorPlanner(atlas)
        apsis_placer: ApsisPlacer = ApsisPlacer(atlas)
        chamfer_placer: ChamferPlacer = ChamferPlacer(atlas)

        # order matters: every pass may rely on all passes above it
        level_passes: tuple[LevelPass, ...] = (
            LevelWallPass(wall_filler, opening_placer),
            LevelApsisPass(apsis_placer),
            LevelChamferPass(chamfer_placer),
            LevelBayPass(BayPlacer(atlas)),
            LevelBracketPass(BracketPlacer(atlas)),
            LevelBalconyPass(LevelBalconyPlacer(atlas, floor_planner)),
            LevelFloorPass(floor_planner, chamfer_placer),
        )
        self._passes: tuple[HousePass, ...] = (
            FoundationPass(foundation_planner),
            WallPass(wall_filler),
            OpeningPass(opening_placer, stair_placer),
            LiftPass(foundation_planner),
            StairPass(stair_placer),
            BalconyPass(BalconyPlanner(atlas)),
            ApsisPass(apsis_placer),
            ChamferPass(chamfer_placer),
            FloorPass(floor_planner, chamfer_placer),
            LevelsPass(
                self._outline_reader,
                LevelFootprintDesigner(),
                LevelStairPlacer(atlas),
                floor_planner,
                level_passes,
            ),
        )
        return None

    def design(self, create_info: BuildingCreateInfo) -> HousePlan:
        """Designs one building.

        Args:
            create_info is the description of the building to design.

        Returns:
            Footprint, rings, floors and levels of the building, carrying the seed it was designed with.
        """
        footprint: Footprint = self._footprint_designer.design(create_info)
        draft: HouseDraft = HouseDraft(
            info=create_info,
            style=self._style,
            footprint=footprint,
            outlines=self._outline_reader.read(footprint),
        )
        for plan_pass in self._passes:
            plan_pass.apply(draft)
        return draft.to_plan()
