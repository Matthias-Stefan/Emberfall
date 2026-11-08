# Copyright (c) 2026 Emberfall. All Rights Reserved.
# bld_architecture/__init__.py

from .bld_architect import (
    Architect,
)
from .bld_building_create_info import (
    BuildingCreateInfo,
)
from .bld_cell_rectangle import (
    CellRectangle,
)
from .bld_contour import (
    ContourCorner,
    ContourRing,
    ContourSegment,
    CornerKind,
)
from .bld_contour_reader import (
    ContourReader,
)
from .bld_footprint import (
    Footprint,
)
from .bld_footprint_colors import (
    FootprintColors,
    footprint_colors,
)
from .bld_house_plan import (
    HousePlan,
)
from .bld_module_atlas import (
    ModuleAtlas,
)
from .bld_placement import (
    Placement,
)
from .bld_side import (
    Side,
)
from .bld_wall_filler import (
    WallFiller,
)
from .bld_wall_ring import (
    WallRing,
)

__all__: list[str] = [
    "Architect",
    "BuildingCreateInfo",
    "CellRectangle",
    "ContourCorner",
    "ContourReader",
    "ContourRing",
    "ContourSegment",
    "CornerKind",
    "Footprint",
    "FootprintColors",
    "HousePlan",
    "ModuleAtlas",
    "Placement",
    "Side",
    "WallFiller",
    "WallRing",

    "footprint_colors",
]
