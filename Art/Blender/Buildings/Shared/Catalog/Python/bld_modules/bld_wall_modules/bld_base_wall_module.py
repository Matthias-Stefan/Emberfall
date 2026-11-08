# Copyright (c) 2026 Emberfall. All Rights Reserved.

from abc import abstractmethod
from dataclasses import dataclass

from bld_modules import BaseModule


@dataclass(frozen=True)
class BaseWallModule(BaseModule):
    """Immutable wall slot module with outer dimensions, not instantiable."""

    width: float
    """Module width along X in m."""
    height: float
    """Module height along Z in m."""
    depth: float
    """Wall thickness along Y in m."""

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
