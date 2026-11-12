# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Everything that is planned for one house: the result and the steps that fill it."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from .bld_house_plan import (
    FoundationPlan,
    HousePlan,
    ModulePlacement,
    ModuleRing,
)
from .bld_steps.bld_step_1_footprint import (
    CellRectangle,
    Footprint,
    FootprintDesigner,
    Side,
)
from .bld_steps.bld_step_2_outline import (
    CornerKind,
    OutlineCorner,
    OutlineReader,
    OutlineRing,
    OutlineSegment,
    Point,
)
from .bld_steps.bld_step_4_walls import (
    WallFiller,
)
from .bld_steps.bld_step_5_openings import (
    OpeningPlacer,
)
from .bld_steps.bld_step_3_foundation import (
    FoundationPlanner,
)
from .bld_steps.bld_step_6_stairs import (
    StairPlacer,
)
from .bld_steps.bld_step_7_floor import (
    FloorPlanner,
)

__all__: list[str] = [
    "CellRectangle",
    "CornerKind",
    "Footprint",
    "FloorPlanner",
    "FootprintDesigner",
    "FoundationPlan",
    "FoundationPlanner",
    "HousePlan",
    "ModulePlacement",
    "ModuleRing",
    "OpeningPlacer",
    "OutlineCorner",
    "OutlineReader",
    "OutlineRing",
    "OutlineSegment",
    "Point",
    "Side",
    "StairPlacer",
    "WallFiller",
]
