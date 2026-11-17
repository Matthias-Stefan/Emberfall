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
    CellRectangle,
    CornerCut,
    CornerKind,
    Footprint,
    FoundationPlan,
    HousePlan,
    LevelPlan,
    ModulePlacement,
    ModuleRing,
    OutlineCorner,
    OutlineRing,
    OutlineSegment,
    Side,
)
from .bld_style import (
    ModuleAtlas,
    Style,
)

__all__: list[str] = [
    "Architect",
    "BalconyCreateInfo",
    "BalconyPlan",
    "BuildingCreateInfo",
    "CellRectangle",
    "CornerCut",
    "CornerKind",
    "ExtensionsCreateInfo",
    "Footprint",
    "FootprintCreateInfo",
    "FoundationCreateInfo",
    "FoundationPlan",
    "HousePlan",
    "LevelPlan",
    "LevelsCreateInfo",
    "ModuleAtlas",
    "ModulePlacement",
    "ModuleRing",
    "OpeningCreateInfo",
    "OutlineCorner",
    "OutlineRing",
    "OutlineSegment",
    "Side",
    "Style",
]
