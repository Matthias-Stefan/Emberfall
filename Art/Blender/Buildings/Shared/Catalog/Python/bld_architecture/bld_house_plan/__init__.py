# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Everything that is planned for one house: the result and the steps that fill it."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from .bld_house_plan import (
    BalconyPlan,
    CornerCut,
    FoundationPlan,
    HousePlan,
    LevelPlan,
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
from .bld_steps.bld_step_7_balconies import (
    BalconyPlanner,
)
from .bld_steps.bld_step_8_floor import (
    FloorPlanner,
)
from .bld_steps.bld_step_9_apsis import (
    ApsisPlacer,
)
from .bld_steps.bld_step_9_bays import (
    BayPlacer,
)
from .bld_steps.bld_step_9_brackets import (
    BracketPlacer,
)
from .bld_steps.bld_step_9_chamfers import (
    ChamferPlacer,
)
from .bld_steps.bld_step_9_level_balconies import (
    LevelBalconyPlacer,
)
from .bld_steps.bld_step_9_level_footprints import (
    LevelFootprintDesigner,
)
from .bld_steps.bld_step_9_level_stairs import (
    LevelStairPlacer,
)
from .bld_steps.bld_step_9_levels import (
    LevelPlanner,
)

__all__: list[str] = [
    "ApsisPlacer",
    "BalconyPlan",
    "BayPlacer",
    "ChamferPlacer",
    "BracketPlacer",
    "BalconyPlanner",
    "CellRectangle",
    "CornerKind",
    "Footprint",
    "FloorPlanner",
    "FootprintDesigner",
    "CornerCut",
    "FoundationPlan",
    "FoundationPlanner",
    "HousePlan",
    "LevelBalconyPlacer",
    "LevelFootprintDesigner",
    "LevelPlan",
    "LevelPlanner",
    "LevelStairPlacer",
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
