# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Wall slot modules with their outer dimensions."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from .bld_opening_wall_module import (
    DoorModule,
    OpeningWallModule,
    WindowModule,
)
from .bld_post_module import (
    PostModule
)
from .bld_wall_module import (
    WallModule
)

__all__: list[str] = [
    "DoorModule",
    "OpeningWallModule",
    "WindowModule",
    "PostModule",
    "WallModule",
]
