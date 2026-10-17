# Copyright (c) 2026 Emberfall. All Rights Reserved.

import bpy

from halftimbered.datatypes import HtHouseParams, HtRect, HtRectKind
from halftimbered.ht_blender_utils import ht_create_box, ht_get_debug_material


def ht_build_foundation(house_params: HtHouseParams, rects: list[HtRect], ground_height: float,
                        collection: bpy.types.Collection) -> None:
    """Builds one stone box per rect.

    Args:
        house_params: Provides grid, offset_x and offset_y.
        rects: Footprint of the house in cells.
        ground_height: Height of the stone layer in meters.
        collection: Collection the boxes are linked to.
    """
    for index, rect in enumerate(rects):
        size_x: float = rect.width * house_params.grid
        size_y: float = rect.depth * house_params.grid

        height: float = ground_height
        if rect.kind == HtRectKind.ANNEX:
            height = house_params.annex.annex_height
        obj: bpy.types.Object = ht_create_box(f"ht_foundation_{index}", size_x, size_y,
                                              height, collection)

        obj.location = (house_params.offset_x + rect.x * house_params.grid,
                        house_params.offset_y + rect.y * house_params.grid, 0.0)

        if rect.kind == HtRectKind.ANNEX:
            obj.data.materials.append(ht_get_debug_material("ht_debug_annex", (1.0, 0.5, 0.0, 1.0)))
        else:
            obj.data.materials.append(ht_get_debug_material("ht_debug_main", (0.5, 0.1, 1.0, 1.0)))
    return None