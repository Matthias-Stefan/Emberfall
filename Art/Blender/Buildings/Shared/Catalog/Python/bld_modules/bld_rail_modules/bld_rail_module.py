# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Rail module, one railing section between two posts."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from ..bld_base_slot_module import BaseSlotModule


@dataclass(frozen=True)
class RailModule(BaseSlotModule):
    """Immutable railing section with a post on both ends, a top rail and a middle rail.

    Local frame: centered in X and Y, floor at Z = 0, the front (-Y) faces outward.
    The inherited width is the span between the two post centers, the depth is the post
    thickness and the height is the railing height. The end posts stick out half a post
    beyond the span, so neighbouring sections and corners share their posts exactly.
    """

    @property
    def name_prefix(self) -> str:
        return "rail"
