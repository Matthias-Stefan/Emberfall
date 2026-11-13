# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Post presets, named width x depth x height in cm."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from bld_modules import PillarModule, PostModule

pillar_40x40x260: PillarModule = PillarModule(width=0.40, height=2.60, depth=0.40)
pillar_40x40x300: PillarModule = PillarModule(width=0.40, height=3.00, depth=0.40)
post_34x34x260: PostModule = PostModule(width=0.34, height=2.60, depth=0.34)
post_40x40x260: PostModule = PostModule(width=0.40, height=2.60, depth=0.40)

assert pillar_40x40x260.name == "pillar_40x40x260"
assert pillar_40x40x300.name == "pillar_40x40x300"
assert post_34x34x260.name == "post_34x34x260"
assert post_40x40x260.name == "post_40x40x260"
