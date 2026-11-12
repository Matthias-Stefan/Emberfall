# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Architect that designs building plans from create infos and a style."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from .bld_architect import (
    Architect,
)
from .bld_create_info import (
    BuildingCreateInfo,
    ExtensionsCreateInfo,
    FootprintCreateInfo,
    OpeningCreateInfo,
)
from .bld_house_plan import (
    CellRectangle,
    Footprint,
    FootprintDesigner,
    HousePlan,
    ModulePlacement,
    ModuleRing,
    OpeningPlacer,
    OutlineCorner,
    OutlineReader,
    OutlineRing,
    OutlineSegment,
    Side,
    WallFiller,
)
from .bld_style import (
    ModuleAtlas,
    Style,
)

__all__: list[str] = [
    "Architect",
    "BuildingCreateInfo",
    "CellRectangle",
    "ExtensionsCreateInfo",
    "Footprint",
    "FootprintCreateInfo",
    "FootprintDesigner",
    "HousePlan",
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
    "Style",
    "WallFiller",
]
