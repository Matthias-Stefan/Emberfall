# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Diagonal wall and window presets for cut corners, named width x depth x height in cm."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import math

from bld_modules import DiagonalWallModule, DiagonalWindowModule

diagonal_wall_141x30x260: DiagonalWallModule = DiagonalWallModule(width=math.sqrt(2.0), height=2.6, depth=0.3)
diagonal_wall_283x30x260: DiagonalWallModule = DiagonalWallModule(width=2.0 * math.sqrt(2.0), height=2.6, depth=0.3)
diagonal_window_141x30x260: DiagonalWindowModule = DiagonalWindowModule(
    width=math.sqrt(2.0), height=2.6, depth=0.3, opening_width=0.7
)
diagonal_window_283x30x260: DiagonalWindowModule = DiagonalWindowModule(
    width=2.0 * math.sqrt(2.0), height=2.6, depth=0.3, opening_width=1.0
)

assert diagonal_wall_141x30x260.name == "diagonal_wall_141x30x260"
assert diagonal_wall_283x30x260.name == "diagonal_wall_283x30x260"
assert diagonal_window_141x30x260.name == "diagonal_window_141x30x260"
assert diagonal_window_283x30x260.name == "diagonal_window_283x30x260"
