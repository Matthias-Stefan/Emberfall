# Copyright (c) 2026 Emberfall. All Rights Reserved.

import math
import random

import bpy

from halftimbered.ht_blender_utils import (
    ht_create_box,
    ht_get_debug_material,
    ht_instance_asset,
    ht_remove_house,
)
from halftimbered.datatypes import (
    HtEdge,
    HtEdgeAxis,
    HtGroundLayerParams,
    HtGroundType,
    HtHouseParams,
    HtPillarKind,
    HtPillarPoint,
    HtRect,
    HtRectKind,
)
from halftimbered.ht_footprint import (
    ht_roll_base_rect,
    ht_roll_wings,
)
from halftimbered.ht_footprint_edges import (
    ht_find_outer_edges,
    ht_find_pillar_points,
    ht_point_touches_kind,
)


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


def ht_build_walls(house_params: HtHouseParams, edges: list[HtEdge],
                   corner_points: list[HtPillarPoint], collection: bpy.types.Collection) -> None:
    """Fills every run of outer edges between two corner pillars with one 160 and n-1 200 walls.

    Args:
        house_params: Provides grid, offset_x and offset_y.
        edges: Outer edges in cells.
        corner_points: Grid points that carry a pillar.
        collection: Collection the walls are linked to.
    """
    grid: float = house_params.grid
    half_pillar: float = 0.2
    pillar_cells: set[tuple[int, int]] = {(point.x, point.y) for point in corner_points}

    # Group unit edges by line: (axis, constant coordinate) -> edges sorted along the line
    lines: dict[tuple[HtEdgeAxis, int], list[HtEdge]] = {}
    for edge in edges:
        constant: int = edge.y if edge.axis == HtEdgeAxis.X else edge.x
        lines.setdefault((edge.axis, constant), []).append(edge)

    wall_index: int = 0
    for (axis, constant), line_edges in lines.items():
        line_edges.sort(key=lambda e: e.x if axis == HtEdgeAxis.X else e.y)

        run: list[HtEdge] = []
        for edge in line_edges:
            start: int = edge.x if axis == HtEdgeAxis.X else edge.y
            if run:
                last: HtEdge = run[-1]
                last_start: int = last.x if axis == HtEdgeAxis.X else last.y
                if start != last_start + 1:
                    run = []  # gap without pillar, drop the broken run
            run.append(edge)

            end_cell: tuple[int, int] = (edge.x + 1, edge.y) if axis == HtEdgeAxis.X else (edge.x, edge.y + 1)
            if end_cell not in pillar_cells:
                continue

            # Run is closed by a pillar: place 160 first, then 200s
            first: HtEdge = run[0]
            height_cm: int = 220 if first.kind == HtRectKind.ANNEX else 260
            cursor: float = (first.x if axis == HtEdgeAxis.X else first.y) * grid + half_pillar
            lengths_cm: list[int] = [160] + [200] * (len(run) - 1)
            for length_cm in lengths_cm:
                length_m: float = length_cm / 100.0
                wall: bpy.types.Object | None = ht_instance_asset(
                    f"SM_ht_wall_stone_{length_cm}x{height_cm}x30_01", f"ht_wall_{wall_index}", collection)
                wall_index += 1
                if wall is not None:
                    center: float = cursor + length_m * 0.5
                    if axis == HtEdgeAxis.X:
                        wall.location = (house_params.offset_x + center,
                                         house_params.offset_y + constant * grid, 0.0)
                    else:
                        wall.location = (house_params.offset_x + constant * grid,
                                         house_params.offset_y + center, 0.0)
                        wall.rotation_euler.z = math.pi / 2
                cursor += length_m
            run = []
    return None


def ht_build_house(house_params: HtHouseParams) -> None:
    """Deletes the old house and builds a fresh one.

    Args:
        house_params: All settings of the house.
    """
    # Phase 1: clean up and create the collection
    ht_remove_house(house_params.house_name)
    collection: bpy.types.Collection = bpy.data.collections.new(house_params.house_name)
    bpy.context.scene.collection.children.link(collection)

    # Phase 2: roll the footprint
    seed: int = house_params.seed if house_params.seed is not None else random.randrange(1_000_000)
    rng: random.Random = random.Random(seed)
    print(f"ht_build_house: seed {seed}")

    base_rect: HtRect | None = ht_roll_base_rect(house_params, rng)
    if base_rect is None:
        return None
    wings: list[HtRect] = ht_roll_wings(base_rect, house_params, rng)
    rects: list[HtRect] = [base_rect] + wings

    # Phase 3: roll the ground type and derive its height
    ground: HtGroundLayerParams = house_params.ground
    ground_type: HtGroundType = HtGroundType.PLINTH
    if rng.random() < ground.stone_floor_chance:
        ground_type = HtGroundType.STONE_FLOOR
    ground_height: float = ground.plinth_height
    if ground_type == HtGroundType.STONE_FLOOR:
        ground_height = ground.floor_height

    # Phase 4: build the geometry
    ht_build_foundation(house_params, rects, ground_height, collection)

    pillar_points: list[HtPillarPoint] = ht_find_pillar_points(rects)
    corner_points: list[HtPillarPoint] = [
        point for point in pillar_points if point.kind != HtPillarKind.EDGE
    ]
    print(f"ht_build_house: {len(corner_points)} corner pillars")
    for index, point in enumerate(corner_points):
        is_annex_only: bool = (
            point.kind != HtPillarKind.STEP
            and ht_point_touches_kind(point, rects, HtRectKind.ANNEX)
            and not ht_point_touches_kind(point, rects, HtRectKind.MAIN)
        )
        asset_name: str = "SM_ht_post_stone_40x220x40_01" if is_annex_only else "SM_ht_post_stone_40x260x40_01"
        post: bpy.types.Object | None = ht_instance_asset(asset_name, f"ht_post_{index}", collection)
        if post is not None:
            post.location = (house_params.offset_x + point.x * house_params.grid,
                             house_params.offset_y + point.y * house_params.grid, 0.0)

    # Walls between the pillars
    edges: list[HtEdge] = ht_find_outer_edges(rects)
    ht_build_walls(house_params, edges, corner_points, collection)

    return None