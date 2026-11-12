# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Door presets, named width x depth x height in cm."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from bld_modules import DoorModule

door_200x30x260: DoorModule = DoorModule(
    width=2.0, height=2.6, depth=0.3, opening_width=1.0, opening_height=2.1
)
door_400x30x260: DoorModule = DoorModule(
    width=4.0, height=2.6, depth=0.3, opening_width=2.0, opening_height=2.1
)

assert door_200x30x260.name == "door_200x30x260"
assert door_400x30x260.name == "door_400x30x260"
