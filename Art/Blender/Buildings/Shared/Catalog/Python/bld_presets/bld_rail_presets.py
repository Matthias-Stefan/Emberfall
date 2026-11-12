# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Rail presets, named span x post thickness x height in cm."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from bld_modules import RailModule


rail_100x8x90: RailModule = RailModule(width=1.0, height=0.90, depth=0.08)
rail_200x8x90: RailModule = RailModule(width=2.0, height=0.90, depth=0.08)

assert rail_100x8x90.name == "rail_100x8x90"
assert rail_200x8x90.name == "rail_200x8x90"
