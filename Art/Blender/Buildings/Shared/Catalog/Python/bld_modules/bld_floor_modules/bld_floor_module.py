# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Floor module, one slab of the floor or ceiling between two levels."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from ..bld_base_slot_module import BaseSlotModule


@dataclass(frozen=True)
class FloorModule(BaseSlotModule):
    """Immutable floor slab, a box with its bottom at Z = 0.

    Local frame: centered in X and Y. The inherited width and depth are the slab size on the
    grid, the height is the slab thickness.
    """

    @property
    def name_prefix(self) -> str:
        return "floor"
