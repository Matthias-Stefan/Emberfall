# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Base class of all wall slot modules, with outer dimensions and validation."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from abc import abstractmethod
from dataclasses import dataclass

from ..bld_base_module import BaseModule

TOLERANCE: float = 1e-4
"""Tolerance for float comparisons in m, 0.1 mm."""

@dataclass(frozen=True)
class BaseWallModule(BaseModule):
    """Immutable wall slot module with outer dimensions, not instantiable."""

    width: float
    """Module width along X in m."""
    height: float
    """Module height along Z in m."""
    depth: float
    """Wall thickness along Y in m."""

    def __post_init__(self) -> None:
        """Runs the validation right after construction, do not override.

        Returns:
            None.
        """
        self.validate()

    def validate(self) -> None:
        """Validates the module, subclasses extend this and call super().validate() first.

        Raises:
            ValueError: If a dimension is not positive.

        Returns:
            None.
        """
        if self.width <= 0.0 or self.height <= 0.0 or self.depth <= 0.0:
            raise ValueError(
                f"Dimensions must be positive, got {self.width} x {self.depth} x {self.height}"
            )

    @property
    @abstractmethod
    def name_prefix(self) -> str:
        """Prefix of the generated asset name."""

    @property
    def name(self) -> str:
        """Asset name with dimensions in cm, ordered X x Y x Z."""
        width_cm: int = round(self.width * 100)
        depth_cm: int = round(self.depth * 100)
        height_cm: int = round(self.height * 100)
        return f"{self.name_prefix}_{width_cm}x{depth_cm}x{height_cm}"
