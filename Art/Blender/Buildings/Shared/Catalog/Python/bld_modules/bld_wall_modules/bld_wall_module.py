# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Plain wall module without an opening."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from ..bld_base_slot_module import BaseSlotModule


@dataclass(frozen=True)
class WallModule(BaseSlotModule):
    """Immutable plain closed wall."""

    @property
    def name_prefix(self) -> str:
        return "wall"
