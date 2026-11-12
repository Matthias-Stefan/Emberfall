# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Stair module that leads from the ground up to a door."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from ..bld_wall_modules import BaseWallModule

MIN_STEPS_FOR_HANDRAIL: int = 3
"""Fewest steps a stair needs to get a handrail, below that the rail would look silly."""


@dataclass(frozen=True)
class StairModule(BaseWallModule):
    """Immutable straight stair, the top step is level with the floor of the door.

    Local frame: centered in X and Y, floor at Z = 0, the steps climb towards +Y,
    so the bottom step is at the front (-Y) and the top step touches the wall.
    The inherited depth is the run of the whole stair, the height is the total rise.
    """

    step_count: int = 2
    """Number of steps, the top one is level with the floor."""
    solid: bool = True
    """Whether the stair is a stone block with cheeks, otherwise an open wooden stair."""
    handrail: bool = False
    """Whether the stair gets a handrail on both sides, ignored below the minimum step count."""

    @property
    def name_prefix(self) -> str:
        return "stair"

    @property
    def has_handrail(self) -> bool:
        """Whether the stair really gets a handrail."""
        return self.handrail and self.step_count >= MIN_STEPS_FOR_HANDRAIL

    @property
    def rise(self) -> float:
        """Height of one step in m."""
        return self.height / self.step_count

    @property
    def tread(self) -> float:
        """Run of one step in m."""
        return self.depth / self.step_count

    @property
    def name(self) -> str:
        """Asset name with dimensions in cm, step count and variant."""
        variant: str = "solid" if self.solid else "open"
        rail: str = "_rail" if self.has_handrail else ""
        return f"{super().name}_{self.step_count}s_{variant}{rail}"

    def validate(self) -> None:
        """Validates that the stair has at least one step.

        Raises:
            ValueError: If step_count is below 1 or the base checks fail.
        """
        super().validate()
        if self.step_count < 1:
            raise ValueError(f"step_count must be >= 1, got {self.step_count}")
