# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Pillar module that carries a platform down to the ground."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from .bld_post_module import PostModule


@dataclass(frozen=True)
class PillarModule(PostModule):
    """Immutable square pillar as high as the platform it carries, never used on a wall corner."""

    @property
    def name_prefix(self) -> str:
        return "pillar"
