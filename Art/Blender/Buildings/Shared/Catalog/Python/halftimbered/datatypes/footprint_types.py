# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass
from enum import Enum


class HtGroundType(Enum):
    """Kind of stone layer at the bottom of the house."""

    PLINTH = 0
    STONE_FLOOR = 1


class HtRectKind(Enum):
    """Role of a rect in the footprint."""

    MAIN = 0
    ANNEX = 1


class HtPillarKind(Enum):
    """Kind of grid point a pillar stands on."""

    CONVEX = 0   # outer corner, 1 neighbor cell occupied
    CONCAVE = 1  # inner corner of an L/T, 3 neighbor cells occupied
    EDGE = 2     # straight edge, 2 neighbor cells side by side
    STEP = 3     # straight edge where main meets annex (height change)


class HtEdgeAxis(Enum):
    """Direction an edge runs along."""

    X = 0  # runs along X, sits on a grid line of constant y
    Y = 1  # runs along Y, sits on a grid line of constant x


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


@dataclass
class HtPillarPoint:
    """Grid point that needs a pillar.

    Attributes:
        x: Grid point X in cells, relative to the house origin.
        y: Grid point Y in cells, relative to the house origin.
        kind: Corner type of the point.
    """

    x: int
    y: int
    kind: HtPillarKind


@dataclass
class HtEdge:
    """Outer edge of a cell on the grid.

    Attributes:
        x: Start grid point X in cells.
        y: Start grid point Y in cells.
        axis: Direction the edge runs along.
        kind: MAIN or ANNEX, taken from the cell that owns the edge.
    """

    x: int
    y: int
    axis: HtEdgeAxis
    kind: HtRectKind