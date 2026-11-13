# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Diagonal wall module with a window opening."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from ..bld_base_slot_module import TOLERANCE
from .bld_diagonal_wall_module import DiagonalWallModule


@dataclass(frozen=True)
class DiagonalWindowModule(DiagonalWallModule):
    """Immutable diagonal wall with a window opening, the opening is centered along the wall."""

    opening_width: float = 0.8
    """Opening width along the wall in m."""
    opening_height: float = 1.2
    """Opening height along Z in m."""
    sill_height: float = 0.9
    """Distance from the floor to the bottom edge of the opening in m."""

    @property
    def name_prefix(self) -> str:
        return "diagonal_window"

    def validate(self) -> None:
        """Validates that the opening fits into the wall.

        Raises:
            ValueError: If the opening has no size, leaves the wall or touches the top.

        Returns:
            None.
        """
        super().validate()
        if self.opening_width <= 0.0 or self.opening_height <= 0.0 or self.sill_height <= TOLERANCE:
            raise ValueError(f"Window opening needs a positive size and a sill in {self.name}")
        if self.opening_width >= self.width - TOLERANCE:
            raise ValueError(f"Window opening leaves no wall at the ends of {self.name}")
        if self.sill_height + self.opening_height > self.height - TOLERANCE:
            raise ValueError(f"Window opening reaches the top of {self.name}")
