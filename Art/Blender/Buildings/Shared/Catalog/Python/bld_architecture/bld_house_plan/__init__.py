# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Data of a planned house: footprint, outline and the placed modules, no planning logic."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from .bld_footprint import (
    CellRectangle,
    Footprint,
    Side,
)
from .bld_house_plan import (
    BalconyPlan,
    CornerCut,
    FoundationPlan,
    HousePlan,
    LevelPlan,
    ModulePlacement,
    ModuleRing,
)
from .bld_outline import (
    CornerKind,
    OutlineCorner,
    OutlineRing,
    OutlineSegment,
    Point,
)

__all__: list[str] = [
    "BalconyPlan",
    "CellRectangle",
    "CornerCut",
    "CornerKind",
    "Footprint",
    "FoundationPlan",
    "HousePlan",
    "LevelPlan",
    "ModulePlacement",
    "ModuleRing",
    "OutlineCorner",
    "OutlineRing",
    "OutlineSegment",
    "Point",
    "Side",
]
