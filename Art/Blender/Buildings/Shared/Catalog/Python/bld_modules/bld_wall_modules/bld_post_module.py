# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Post module that stands on the corners of a wall ring."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from .bld_base_wall_module import TOLERANCE, BaseWallModule


@dataclass(frozen=True)
class PostModule(BaseWallModule):
    """Immutable square post that covers a wall corner."""

    @property
    def name_prefix(self) -> str:
        return "post"

    def validate(self) -> None:
        """Validates that the post has a square footprint.

        Raises:
            ValueError: If width and depth differ or the base checks fail.

        Returns:
            None.
        """
        super().validate()  # base checks first
        if abs(self.width - self.depth) > TOLERANCE:
            raise ValueError(f"A post needs a square footprint, got {self.width} x {self.depth}")
