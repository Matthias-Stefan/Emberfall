# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Window module, a wall slot with a window opening."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from ..bld_base_wall_module import TOLERANCE
from .bld_opening_wall_module import OpeningWallModule


@dataclass(frozen=True)
class WindowModule(OpeningWallModule):
    """Immutable wall with a window opening above a sill."""

    opening_height: float = 1.2
    """Opening height along Z in m."""
    sill_height: float = 0.9
    """Distance from the floor to the bottom edge of the opening in m."""

    @property
    def name_prefix(self) -> str:
        return "window"

    def validate(self) -> None:
        """Validates that the opening sits above the floor.

        Raises:
            ValueError: If sill_height is 0 or the base checks fail.

        Returns:
            None.
        """
        super().validate()  # base and opening checks first
        if self.sill_height <= TOLERANCE:
            raise ValueError(f"A window needs sill_height > 0, got {self.sill_height}")
