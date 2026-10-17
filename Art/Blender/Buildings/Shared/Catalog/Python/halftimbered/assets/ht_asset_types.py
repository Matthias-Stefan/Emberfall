# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass
from enum import Enum
from typing import TypeVar

E = TypeVar("E", bound=Enum)


class HtAssetLayer(Enum):
    """Where in the house an asset sits (Layer)."""

    FOUNDATION = "foundation"


class HtAssetKind(Enum):
    """What an asset is (Art)."""

    WALL = "wall"
    POST = "post"


class HtAssetMaterial(Enum):
    """What an asset is made of (Material)."""

    STONE = "stone"


def ht_parse_enum(enum_type: type[E], raw: str) -> E | None:
    """Converts a property string into a member of the given enum.

    Args:
        enum_type: Enum to look the value up in.
        raw: Property value, case and surrounding whitespace are ignored.

    Returns:
        The member, or None if the value is not part of the enum.
    """
    value: str = raw.strip().lower()
    for member in enum_type:
        if member.value == value:
            return member
    return None


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
