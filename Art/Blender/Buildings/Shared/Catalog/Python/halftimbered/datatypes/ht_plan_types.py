# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass

from halftimbered.assets import HtAssetDef


@dataclass(frozen=True)
class HtPlacement:
    """One asset instance in the house plan.

    Attributes:
        asset: Catalog asset to instance.
        x: Position X in meters, relative to the house origin.
        y: Position Y in meters, relative to the house origin.
        z: Position Z in meters, 0 for the ground layer.
        rotation_z: Rotation around Z in radians.
    """

    asset: HtAssetDef
    x: float
    y: float
    z: float = 0.0
    rotation_z: float = 0.0