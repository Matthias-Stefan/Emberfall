# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass
from enum import Enum


class HtRectKind(Enum):
    """Role of a rect in the footprint."""

    MAIN = 0
    ANNEX = 1


@dataclass
class HtRect:
    """Rectangle on the cell grid, relative to the house origin.

    Attributes:
        x: Minimum cell X, relative to the house origin.
        y: Minimum cell Y, relative to the house origin.
        width: Size in cells along X.
        depth: Size in cells along Y.
        kind: Role of the rect, MAIN unless a wing qualifies as annex.
    """

    x: int
    y: int
    width: int
    depth: int
    kind: HtRectKind = HtRectKind.MAIN