# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Base class of wall modules with an opening."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from ...bld_base_slot_module import TOLERANCE, BaseSlotModule


@dataclass(frozen=True)
class OpeningWallModule(BaseSlotModule):
    """Immutable wall slot module with one rectangular opening, not instantiable."""

    opening_width: float = 1.0
    """Opening width along X in m."""
    opening_height: float = 2.1
    """Opening height along Z in m."""
    sill_height: float = 0.0
    """Distance from the floor to the bottom edge of the opening in m, 0 for a door."""
    opening_offset: float | None = None
    """Distance from the left module edge to the left opening edge in m, None centers the opening."""

    @property
    def head_height(self) -> float:
        """Distance from the floor to the top edge of the opening in m."""
        return self.sill_height + self.opening_height

    @property
    def resolved_opening_offset(self) -> float:
        """Distance from the left module edge to the left opening edge in m, never None."""
        if self.opening_offset is None:
            # centered: same wall width on both sides of the opening
            return (self.width - self.opening_width) * 0.5
        return self.opening_offset

    def validate(self) -> None:
        """Validates that the opening fits into the module.

        Raises:
            ValueError: If the opening has no size, leaves the module or touches the top.

        Returns:
            None.
        """
        super().validate()
        if self.opening_width <= 0.0 or self.opening_height <= 0.0:
            raise ValueError(f"Opening needs a positive size in {self.name}")
        if self.sill_height < 0.0:
            raise ValueError(f"sill_height must be >= 0, got {self.sill_height}")
        if self.opening_offset is not None and self.opening_offset < 0.0:
            raise ValueError(f"opening_offset must be >= 0 or None, got {self.opening_offset}")
        if self.head_height > self.height - TOLERANCE:
            # no wall left above the opening, so there would be no lintel
            raise ValueError(f"Opening reaches the top of {self.name}")
        if self.resolved_opening_offset + self.opening_width > self.width + TOLERANCE:
            raise ValueError(f"Opening leaves the module {self.name} on the right side")
