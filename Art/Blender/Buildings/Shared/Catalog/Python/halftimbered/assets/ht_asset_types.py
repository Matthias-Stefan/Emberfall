# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass

from halftimbered.assets.ht_asset_enums import (
    HtAssetKind,
    HtAssetLayer,
    HtAssetMaterial,
)


@dataclass(frozen=True)
class HtAssetDef:
    """One catalog asset, built from its object name and properties.

    Attributes:
        name: Full object name, e.g. SM_ht_wall_160x220x30_01.
        kind: Art of the asset, from the "ht_kind" property.
        material: Material of the asset, from the "ht_material" property.
        layer: Layer of the asset, from the "ht_layer" property.
        length_cm: First number of the name, size along the run.
        height_cm: Second number of the name, size along Z.
        depth_cm: Third number of the name, thickness of the asset.
        variant: Trailing number of the name, 1 for _01.
    """

    name: str
    kind: HtAssetKind
    material: HtAssetMaterial
    layer: HtAssetLayer
    length_cm: int
    height_cm: int
    depth_cm: int
    variant: int

    def matches(self, kind: HtAssetKind | None = None,
                material: HtAssetMaterial | None = None,
                layer: HtAssetLayer | None = None) -> bool:
        """Checks the asset against optional category filters.

        Args:
            kind: Required kind, None accepts any.
            material: Required material, None accepts any.
            layer: Required layer, None accepts any.

        Returns:
            True if every given filter matches.
        """
        if kind is not None and self.kind != kind:
            return False
        if material is not None and self.material != material:
            return False
        if layer is not None and self.layer != layer:
            return False
        return True
