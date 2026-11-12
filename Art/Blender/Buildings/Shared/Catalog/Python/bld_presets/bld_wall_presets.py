# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Wall presets, named width x depth x height in cm."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from bld_modules import WallModule

wall_100x30x260: WallModule = WallModule(width=1.0, height=2.6, depth=0.3)
wall_200x30x260: WallModule = WallModule(width=2.0, height=2.6, depth=0.3)
wall_400x30x260: WallModule = WallModule(width=4.0, height=2.6, depth=0.3)
wall_600x30x260: WallModule = WallModule(width=6.0, height=2.6, depth=0.3)

assert wall_100x30x260.name == "wall_100x30x260"
assert wall_200x30x260.name == "wall_200x30x260"
assert wall_400x30x260.name == "wall_400x30x260"
assert wall_600x30x260.name == "wall_600x30x260"
