# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Wall modules with an opening: doors and windows."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from .bld_door_module import (
    DoorModule,
)
from .bld_opening_wall_module import (
    OpeningWallModule
)
from .bld_window_module import (
    WindowModule
)

__all__: list[str] = [
    "DoorModule",
    "OpeningWallModule",
    "WindowModule",
]
