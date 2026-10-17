# Copyright (c) 2026 Emberfall. All Rights Reserved.

import bpy

from halftimbered.datatypes import HtHouseParams, HtPlacement
from halftimbered.ht_blender_utils import ht_instance_asset


def ht_build_placements(house_params: HtHouseParams, placements: list[HtPlacement],
                        collection: bpy.types.Collection) -> list[bpy.types.Object]:
    """Instances one object per placement and moves it to its world position.

    Args:
        house_params: Provides offset_x and offset_y, added to the house-relative positions.
        placements: Plan entries, positions in meters relative to the house origin.
        collection: Collection the objects are linked to.

    Returns:
        The created objects, placements whose asset is missing in Blender are skipped.
    """
    objects: list[bpy.types.Object] = []
    for index, placement in enumerate(placements):
        name: str = f"ht_{placement.asset.kind.value}_{index}"
        obj: bpy.types.Object | None = ht_instance_asset(placement.asset.name, name, collection)
        if obj is None:
            continue

        obj.location = (house_params.offset_x + placement.x,
                        house_params.offset_y + placement.y,
                        placement.z)
        obj.rotation_euler.z = placement.rotation_z
        objects.append(obj)
    return objects