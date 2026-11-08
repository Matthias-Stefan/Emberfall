# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass

from .bld_base_wall_module import BaseWallModule


@dataclass(frozen=True)
class PostModule(BaseWallModule):
    """Immutable square post that covers a wall corner."""

    @property
    def name_prefix(self) -> str:
        return "post"
