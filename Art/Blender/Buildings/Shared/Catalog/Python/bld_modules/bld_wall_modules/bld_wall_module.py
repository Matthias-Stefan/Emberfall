# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Plain wall module without an opening."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from .bld_base_wall_module import BaseWallModule


@dataclass(frozen=True)
class WallModule(BaseWallModule):
    """Immutable plain closed wall."""

    @property
    def name_prefix(self) -> str:
        return "wall"
