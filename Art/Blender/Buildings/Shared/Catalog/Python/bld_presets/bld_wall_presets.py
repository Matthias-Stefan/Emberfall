# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Wall presets, named width x depth x height in cm."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from bld_modules import ArcWallModule, ArcWindowModule, BayWallModule, BracketModule, WallModule

arc_wall_100x30x260_b50: ArcWallModule = ArcWallModule(width=1.0, height=2.6, depth=0.3, bulge=0.5)
arc_wall_200x30x260_b50: ArcWallModule = ArcWallModule(width=2.0, height=2.6, depth=0.3, bulge=0.5)
bay_wall_50x30x260: BayWallModule = BayWallModule(width=0.5, height=2.6, depth=0.3)
bracket_40x14x50: BracketModule = BracketModule(width=0.4, height=0.5, depth=0.14)
bracket_50x14x50: BracketModule = BracketModule(width=0.5, height=0.5, depth=0.14)
wall_100x30x260: WallModule = WallModule(width=1.0, height=2.6, depth=0.3)
wall_200x30x260: WallModule = WallModule(width=2.0, height=2.6, depth=0.3)
wall_400x30x260: WallModule = WallModule(width=4.0, height=2.6, depth=0.3)
wall_600x30x260: WallModule = WallModule(width=6.0, height=2.6, depth=0.3)

assert arc_wall_100x30x260_b50.name == "arc_wall_100x30x260_b50"
assert arc_wall_200x30x260_b50.name == "arc_wall_200x30x260_b50"
assert bay_wall_50x30x260.name == "bay_wall_50x30x260"
assert bracket_40x14x50.name == "bracket_40x14x50"
assert bracket_50x14x50.name == "bracket_50x14x50"
assert wall_100x30x260.name == "wall_100x30x260"
assert wall_200x30x260.name == "wall_200x30x260"
assert wall_400x30x260.name == "wall_400x30x260"
assert wall_600x30x260.name == "wall_600x30x260"
