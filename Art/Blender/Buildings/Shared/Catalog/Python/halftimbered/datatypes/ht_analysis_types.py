# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass
from enum import Enum

from halftimbered.datatypes.ht_footprint_types import HtRectKind


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


@dataclass(frozen=True)
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


@dataclass(frozen=True)
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