# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Immutable module descriptions: walls, doors, windows, posts, rails, stairs and floors."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from .bld_base_module import (
    BaseModule,
)
from .bld_base_slot_module import (
    BaseSlotModule,
    TOLERANCE,
)

from .bld_wall_modules import (
    ArcWallModule,
    ArcWindowModule,
    BayWallModule,
    DoorModule,
    OpeningWallModule,
    PillarModule,
    PostModule,
    WallModule,
    WindowModule,
)

from .bld_floor_modules import (
    ArcFloorModule,
    FloorModule,
)
from .bld_rail_modules import (
    RailModule,
)
from .bld_stair_modules import (
    StairModule,
)

__all__: list[str] = [
    "ArcFloorModule",
    "ArcWallModule",
    "ArcWindowModule",
    "BayWallModule",
    "BaseModule",
    "BaseSlotModule",
    "DoorModule",
    "FloorModule",
    "OpeningWallModule",
    "PillarModule",
    "PostModule",
    "RailModule",
    "StairModule",
    "WallModule",
    "WindowModule",

    "TOLERANCE",
]
