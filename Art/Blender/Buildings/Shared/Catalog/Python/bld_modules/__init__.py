# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Immutable module descriptions: walls, doors, windows, posts and stairs."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from .bld_base_module import (
    BaseModule,
)

from .bld_wall_modules import (
    BaseWallModule,
    DoorModule,
    OpeningWallModule,
    PostModule,
    StairModule,
    WallModule,
    WindowModule,

    TOLERANCE,
)

__all__: list[str] = [
    "BaseModule",
    "BaseWallModule",
    "DoorModule",
    "OpeningWallModule",
    "PostModule",
    "StairModule",
    "WallModule",
    "WindowModule",

    "TOLERANCE",
]
