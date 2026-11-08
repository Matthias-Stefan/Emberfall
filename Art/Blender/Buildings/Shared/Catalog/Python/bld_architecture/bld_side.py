# Copyright (c) 2026 Emberfall. All Rights Reserved.

from enum import Enum


class Side(Enum):
    """Side of a rectangle in cell space, Y points up."""

    NORTH = "north"
    EAST = "east"
    SOUTH = "south"
    WEST = "west"
