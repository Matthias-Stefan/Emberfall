# Copyright (c) 2026 Emberfall. All Rights Reserved.

from halftimbered.assets import HtAssetDef, HtAssetKind, HtAssetLayer, HtAssetCatalog
from halftimbered.datatypes import (
    HtHouseParams,
    HtPillarKind,
    HtPillarPoint,
    HtPlacement,
)


def _find_post(assets: list[HtAssetDef], height_cm: int) -> HtAssetDef | None:
    """Finds a foundation post of the given height.

    Args:
        assets: Discovered catalog assets.
        height_cm: Required post height in centimeters.

    Returns:
        The first matching asset, or None (with a warning) if there is none.
    """
    for asset in assets:
        if asset.matches(kind=HtAssetKind.POST, layer=HtAssetLayer.FOUNDATION) \
                and asset.height_cm == height_cm:
            return asset
    print(f"_find_post: no foundation post with height {height_cm} cm")
    return None


def ht_plan_pillars(house_params: HtHouseParams, pillar_points: list[HtPillarPoint],
                    catalog: HtAssetCatalog, main_height_cm: int,
                    annex_height_cm: int) -> list[HtPlacement]:
    """Plans one post per corner point, EDGE points get none.

    Args:
        house_params: Provides grid.
        pillar_points: All analysed grid points, EDGE ones are skipped here.
        catalog: Catalog the posts are taken from.
        main_height_cm: Post height for points that touch a main rect.
        annex_height_cm: Post height for points that only touch annex rects.

    Returns:
        One placement per post, positions in meters relative to the house origin.
    """
    placements: list[HtPlacement] = []
    for point in pillar_points:
        if point.kind == HtPillarKind.EDGE:
            continue

        height_cm: int = annex_height_cm if point.annex_only else main_height_cm

        asset: HtAssetDef | None = catalog.first(
            kind=HtAssetKind.POST, layer=HtAssetLayer.FOUNDATION, height_cm=height_cm)
        if asset is None:
            continue

        placements.append(HtPlacement(asset, point.x * house_params.grid, point.y * house_params.grid))
    return placements