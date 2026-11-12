# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Post presets, named width x depth x height in cm."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from bld_modules import PostModule


post_34x34x260: PostModule = PostModule(width=0.34, height=2.60, depth=0.34)

assert post_34x34x260.name == "post_34x34x260"
