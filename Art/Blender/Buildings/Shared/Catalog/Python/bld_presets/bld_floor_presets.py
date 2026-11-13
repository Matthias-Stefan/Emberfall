# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Floor presets, named width x depth x thickness in cm."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from bld_modules import ArcFloorModule, FloorModule


arc_floor_100x50x30: ArcFloorModule = ArcFloorModule(width=1.0, height=0.30, depth=0.5)
arc_floor_200x50x30: ArcFloorModule = ArcFloorModule(width=2.0, height=0.30, depth=0.5)
floor_100x100x30: FloorModule = FloorModule(width=1.0, height=0.30, depth=1.0)
floor_100x50x30: FloorModule = FloorModule(width=1.0, height=0.30, depth=0.5)
floor_50x50x30: FloorModule = FloorModule(width=0.5, height=0.30, depth=0.5)

assert arc_floor_100x50x30.name == "arc_floor_100x50x30"
assert arc_floor_200x50x30.name == "arc_floor_200x50x30"
assert floor_100x100x30.name == "floor_100x100x30"
assert floor_100x50x30.name == "floor_100x50x30"
assert floor_50x50x30.name == "floor_50x50x30"
