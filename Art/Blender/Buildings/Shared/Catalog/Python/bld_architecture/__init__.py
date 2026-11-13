# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Architect that designs building plans from create infos and a style."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from .bld_architect import (
    Architect,
)
from .bld_create_info import (
    BalconyCreateInfo,
    BuildingCreateInfo,
    ExtensionsCreateInfo,
    FootprintCreateInfo,
    FoundationCreateInfo,
    LevelsCreateInfo,
    OpeningCreateInfo,
)
from .bld_house_plan import (
    BalconyPlan,
    BalconyPlanner,
    BayPlacer,
    CellRectangle,
    Footprint,
    FloorPlanner,
    FootprintDesigner,
    FoundationPlan,
    FoundationPlanner,
    HousePlan,
    LevelBalconyPlacer,
    LevelFootprintDesigner,
    LevelPlan,
    LevelPlanner,
    LevelStairPlacer,
    ModulePlacement,
    ModuleRing,
    OpeningPlacer,
    OutlineCorner,
    OutlineReader,
    OutlineRing,
    OutlineSegment,
    Side,
    StairPlacer,
    WallFiller,
)
from .bld_style import (
    ModuleAtlas,
    Style,
)

__all__: list[str] = [
    "BalconyCreateInfo",
    "BalconyPlan",
    "BalconyPlanner",
    "BayPlacer",
    "Architect",
    "BuildingCreateInfo",
    "CellRectangle",
    "ExtensionsCreateInfo",
    "Footprint",
    "FootprintCreateInfo",
    "FoundationCreateInfo",
    "FloorPlanner",
    "FootprintDesigner",
    "FoundationPlan",
    "FoundationPlanner",
    "HousePlan",
    "LevelBalconyPlacer",
    "LevelFootprintDesigner",
    "LevelPlan",
    "LevelPlanner",
    "LevelStairPlacer",
    "LevelsCreateInfo",
    "ModuleAtlas",
    "ModulePlacement",
    "ModuleRing",
    "OpeningCreateInfo",
    "OpeningPlacer",
    "OutlineCorner",
    "OutlineReader",
    "OutlineRing",
    "OutlineSegment",
    "Side",
    "StairPlacer",
    "Style",
    "WallFiller",
]
