# Copyright (c) 2026 Emberfall. All Rights Reserved.

import random

import bpy

from halftimbered.assets import HtAssetCatalog
from halftimbered.builder import ht_build_foundation, ht_build_placements
from halftimbered.datatypes import (
    HtEdge,
    HtGroundLayerParams,
    HtGroundType,
    HtHouseParams,
    HtPillarKind,
    HtPillarPoint,
    HtPlacement,
    HtRect,
    HtWallRun,
)
from halftimbered.ht_blender_utils import ht_discover_assets, ht_remove_house
from halftimbered.ht_footprint_roll import ht_roll_base_rect, ht_roll_wings
from halftimbered.ht_footprint_analysis import ht_find_outer_edges, ht_find_pillar_points
from halftimbered.layout import ht_find_wall_runs, ht_plan_pillars, ht_plan_walls

CATALOG_COLLECTION: str = "HalfTimberedCollection"
MAIN_HEIGHT_CM: int = 260
ANNEX_HEIGHT_CM: int = 220


def _create_collection(house_name: str) -> bpy.types.Collection:
    """Deletes the old house and creates a fresh collection.

    Args:
        house_name: Name of the house collection.

    Returns:
        The new collection, linked to the scene.
    """
    ht_remove_house(house_name)
    collection: bpy.types.Collection = bpy.data.collections.new(house_name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def _roll_footprint(house_params: HtHouseParams, rng: random.Random) -> list[HtRect] | None:
    """Rolls the base rect and its wings.

    Args:
        house_params: Provides grid, base and wing limits.
        rng: Random source of the house.

    Returns:
        Base rect first, then the wings; None if no base rect fits the limits.
    """
    base_rect: HtRect | None = ht_roll_base_rect(house_params, rng)
    if base_rect is None:
        return None
    wings: list[HtRect] = ht_roll_wings(base_rect, house_params, rng)
    return [base_rect] + wings


def _roll_ground_height(ground: HtGroundLayerParams, rng: random.Random) -> float:
    """Rolls the ground type and returns its height.

    Args:
        ground: Settings of the stone layer.
        rng: Random source of the house.

    Returns:
        Plinth or stone floor height in meters.
    """
    ground_type: HtGroundType = HtGroundType.PLINTH
    if rng.random() < ground.stone_floor_chance:
        ground_type = HtGroundType.STONE_FLOOR
    if ground_type == HtGroundType.STONE_FLOOR:
        return ground.floor_height
    return ground.plinth_height


def ht_build_house(house_params: HtHouseParams) -> None:
    """Deletes the old house and builds a fresh one.

    Args:
        house_params: All settings of the house.
    """
    collection: bpy.types.Collection = _create_collection(house_params.house_name)

    seed: int = house_params.seed if house_params.seed is not None else random.randrange(1_000_000)
    rng: random.Random = random.Random(seed)
    print(f"ht_build_house: seed {seed}")

    # Same roll order as before, otherwise the seeds produce different houses
    rects: list[HtRect] | None = _roll_footprint(house_params, rng)
    if rects is None:
        return None
    ground_height: float = _roll_ground_height(house_params.ground, rng)

    catalog: HtAssetCatalog = HtAssetCatalog(ht_discover_assets(CATALOG_COLLECTION))
    pillar_points: list[HtPillarPoint] = ht_find_pillar_points(rects)
    corner_points: list[HtPillarPoint] = [p for p in pillar_points if p.kind != HtPillarKind.EDGE]
    edges: list[HtEdge] = ht_find_outer_edges(rects)
    wall_runs: list[HtWallRun] = ht_find_wall_runs(edges, corner_points)

    pillar_plan: list[HtPlacement] = ht_plan_pillars(
        house_params, pillar_points, catalog, MAIN_HEIGHT_CM, ANNEX_HEIGHT_CM)
    wall_plan: list[HtPlacement] = ht_plan_walls(
        house_params, wall_runs, catalog, MAIN_HEIGHT_CM, ANNEX_HEIGHT_CM)
    print(f"ht_build_house: {len(corner_points)} corner pillars, {len(wall_plan)} walls")

    ht_build_foundation(house_params, rects, ground_height, collection)
    ht_build_placements(house_params, pillar_plan, collection)
    ht_build_placements(house_params, wall_plan, collection)
    return None