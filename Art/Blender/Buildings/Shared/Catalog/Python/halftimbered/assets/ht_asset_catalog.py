# Copyright (c) 2026 Emberfall. All Rights Reserved.

import random

from halftimbered.assets.ht_asset_enums import (
    HtAssetKind,
    HtAssetLayer,
    HtAssetMaterial,
)
from halftimbered.assets.ht_asset_types import HtAssetDef


class HtAssetCatalog:
    """Read-only collection of catalog assets with category and size queries."""

    def __init__(self, assets: list[HtAssetDef]) -> None:
        """Stores the assets, sorted so that results are deterministic.

        Args:
            assets: Discovered catalog assets.
        """
        self._assets: tuple[HtAssetDef, ...] = tuple(
            sorted(assets, key=lambda asset: (asset.name, asset.variant)))


    def query(self, *, kind: HtAssetKind | None = None,
              material: HtAssetMaterial | None = None,
              layer: HtAssetLayer | None = None,
              length_cm: int | None = None,
              height_cm: int | None = None,
              depth_cm: int | None = None) -> list[HtAssetDef]:
        """Returns all assets that match every given filter.

        Args:
            kind: Required kind, None accepts any.
            material: Required material, None accepts any.
            layer: Required layer, None accepts any.
            length_cm: Required length, None accepts any.
            height_cm: Required height, None accepts any.
            depth_cm: Required depth, None accepts any.

        Returns:
            Matching assets in stable order, empty if nothing fits.
        """
        result: list[HtAssetDef] = []
        for asset in self._assets:
            if not asset.matches(kind=kind, material=material, layer=layer):
                continue
            if length_cm is not None and asset.length_cm != length_cm:
                continue
            if height_cm is not None and asset.height_cm != height_cm:
                continue
            if depth_cm is not None and asset.depth_cm != depth_cm:
                continue
            result.append(asset)
        return result


    def first(self, **filters: object) -> HtAssetDef | None:
        """Returns the first match, or None with a warning.

        Args:
            **filters: Same filters as @c query.

        Returns:
            The first matching asset, or None if nothing fits.
        """
        found: list[HtAssetDef] = self.query(**filters)  # type: ignore[arg-type]
        if not found:
            print(f"HtAssetCatalog.first: no asset for {filters}")
            return None
        return found[0]


    def pick(self, rng: random.Random, **filters: object) -> HtAssetDef | None:
        """Picks a random match, or None with a warning.

        Args:
            rng: Random source for the variation.
            **filters: Same filters as @c query.

        Returns:
            One matching asset, or None if nothing fits.
        """
        found: list[HtAssetDef] = self.query(**filters)  # type: ignore[arg-type]
        if not found:
            print(f"HtAssetCatalog.pick: no asset for {filters}")
            return None
        if len(found) == 1:
            # No rng call for a single candidate, so existing seeds stay untouched
            return found[0]
        return rng.choice(found)