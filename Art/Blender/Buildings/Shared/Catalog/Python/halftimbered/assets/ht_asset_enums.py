# Copyright (c) 2026 Emberfall. All Rights Reserved.

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
    DOOR = "door"


class HtAssetMaterial(Enum):
    """What an asset is made of (Material)."""

    STONE      = "stone"
    WOOD       = "wood"
    STONE_WOOD = "stone_wood"


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