# Copyright (c) 2026 Emberfall. All Rights Reserved.

from .bld_base_module import BaseModule

from dataclasses import dataclass


class BaseWallModule(BaseModule):
    """Wall module with fixed outer dimensions."""

    def __init__(self, width: float, height: float, depth: float) -> None:
        """Creates a wall module.

        Args:
            width: Module width along X in m.
            height: Module height along Z in m.
            depth: Wall thickness along Y in m.

        Returns:
            None.
        """
        self.width: float = width
        self.height: float = height
        self.depth: float = depth
        return None


@dataclass(frozen=True)
class ExteriorPlaceholderWallModule(BaseWallModule):
    """Immutable placeholder exterior wall."""

    width: float
    """Module width along X in m."""
    height: float
    """Module height along Z in m."""
    depth: float
    """Wall thickness along Y in m."""
