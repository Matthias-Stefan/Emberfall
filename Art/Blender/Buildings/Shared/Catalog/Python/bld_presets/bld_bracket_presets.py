# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Bracket presets that carry bays, named width x depth x height in cm."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from bld_modules import BracketModule

bracket_40x14x50: BracketModule = BracketModule(width=0.4, height=0.5, depth=0.14)
bracket_50x14x50: BracketModule = BracketModule(width=0.5, height=0.5, depth=0.14)

assert bracket_40x14x50.name == "bracket_40x14x50"
assert bracket_50x14x50.name == "bracket_50x14x50"
