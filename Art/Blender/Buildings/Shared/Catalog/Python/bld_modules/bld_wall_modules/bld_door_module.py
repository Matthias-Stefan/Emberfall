# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass
from typing import ClassVar

from .bld_base_wall_module import BaseWallModule


@dataclass(frozen=True)
class DoorModule(BaseWallModule):
    """Immutable wall with a door opening."""

    opening_width: float = 1.0
    """Opening width along X in m."""
    opening_height: float = 2.1
    """Opening height along Z in m."""

    @property
    def name_prefix(self) -> str:
        return "door"
