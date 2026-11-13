# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Diagonal timber brace that carries a bay from the wall below."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from ..bld_base_slot_module import BaseSlotModule


@dataclass(frozen=True)
class BracketModule(BaseSlotModule):
    """Immutable brace in the XZ plane, its low end sits on the wall and its high end under the bay.

    Local frame: centered in X and Y, floor at Z = 0, the low end lies at -X and the high end
    at +X. The inherited width is the projection, the inherited depth is the thickness of the beam.
    """

    @property
    def name_prefix(self) -> str:
        return "bracket"
