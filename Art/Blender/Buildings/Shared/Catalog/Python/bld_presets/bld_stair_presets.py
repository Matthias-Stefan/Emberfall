# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Stair presets, named width x run x rise in cm plus step count and variant."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from bld_modules import StairModule


stair_200x60x40_2s_solid: StairModule = StairModule(
    width=2.0, height=0.40, depth=0.60, step_count=2, solid=True
)
stair_200x60x40_2s_open: StairModule = StairModule(
    width=2.0, height=0.40, depth=0.60, step_count=2, solid=False
)
stair_200x90x60_3s_solid_rail: StairModule = StairModule(
    width=2.0, height=0.60, depth=0.90, step_count=3, solid=True, handrail=True
)
stair_200x90x60_3s_open_rail: StairModule = StairModule(
    width=2.0, height=0.60, depth=0.90, step_count=3, solid=False, handrail=True
)
stair_400x60x40_2s_solid: StairModule = StairModule(
    width=4.0, height=0.40, depth=0.60, step_count=2, solid=True
)

assert stair_200x60x40_2s_solid.name == "stair_200x60x40_2s_solid"
assert stair_200x60x40_2s_open.name == "stair_200x60x40_2s_open"
assert stair_200x90x60_3s_solid_rail.name == "stair_200x90x60_3s_solid_rail"
assert stair_200x90x60_3s_open_rail.name == "stair_200x90x60_3s_open_rail"
assert stair_400x60x40_2s_solid.name == "stair_400x60x40_2s_solid"
