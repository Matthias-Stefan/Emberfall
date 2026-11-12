# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Immutable module descriptions: walls, doors, windows, posts, stairs and floors."""

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
    DoorModule,
    OpeningWallModule,
    PostModule,
    WallModule,
    WindowModule,
)

from .bld_floor_modules import (
    FloorModule,
)
from .bld_stair_modules import (
    StairModule,
)

__all__: list[str] = [
    "BaseModule",
    "BaseSlotModule",
    "DoorModule",
    "FloorModule",
    "OpeningWallModule",
    "PostModule",
    "StairModule",
    "WallModule",
    "WindowModule",

    "TOLERANCE",
]
