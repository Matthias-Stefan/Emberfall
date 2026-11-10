# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass

from ..bld_base_wall_module import TOLERANCE
from .bld_opening_wall_module import OpeningWallModule


@dataclass(frozen=True)
class DoorModule(OpeningWallModule):
    """Immutable wall with a door opening that reaches down to the floor."""

    @property
    def name_prefix(self) -> str:
        return "door"

    def validate(self) -> None:
        """Validates that the opening reaches the floor.

        Raises:
            ValueError: If sill_height is not 0 or the base checks fail.

        Returns:
            None.
        """
        super().validate()  # base and opening checks first
        if self.sill_height > TOLERANCE:
            raise ValueError(f"A door needs sill_height 0, got {self.sill_height}")
        return None
