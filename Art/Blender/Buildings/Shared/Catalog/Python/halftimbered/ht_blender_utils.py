# Copyright (c) 2026 Emberfall. All Rights Reserved.

import bmesh
import bpy

from halftimbered.assets import (
    HtAssetDef,
    HtAssetKind,
    HtAssetLayer,
    HtAssetMaterial,
    ht_parse_enum,
)


def ht_remove_house(house_name: str) -> None:
    """Deletes the house collection with all its objects and meshes.

    Args:
        house_name: Name of the collection to delete.
    """
    collection: bpy.types.Collection | None = bpy.data.collections.get(house_name)
    if collection is None:
        return None

    for obj in list(collection.objects):
        mesh: bpy.types.Mesh | None = obj.data
        bpy.data.objects.remove(obj)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)

    bpy.data.collections.remove(collection)
    return None


def ht_create_box(name: str, size_x: float, size_y: float, size_z: float,
                  collection: bpy.types.Collection) -> bpy.types.Object:
    """Creates a box with its origin at the bottom corner (min X, min Y, Z = 0).

    Args:
        name: Object and mesh name.
        size_x: Size along X in meters.
        size_y: Size along Y in meters.
        size_z: Size along Z in meters.
        collection: Collection the object is linked to.

    Returns:
        The created object.
    """
    mesh: bpy.types.Mesh = bpy.data.meshes.new(name)
    bm: bmesh.types.BMesh = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(size_x, size_y, size_z), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(size_x * 0.5, size_y * 0.5, size_z * 0.5), verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()

    obj: bpy.types.Object = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def ht_get_debug_material(name: str, color: tuple[float, float, float, float]) -> bpy.types.Material:
    """Returns the debug material of this name, created once; its colors are always refreshed.

    Args:
        name: Material name.
        color: RGBA color.

    Returns:
        The material.
    """
    material: bpy.types.Material | None = bpy.data.materials.get(name)
    if material is None:
        material = bpy.data.materials.new(name)

    material.diffuse_color = color
    material.use_nodes = True
    bsdf: bpy.types.Node | None = material.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
    return material


def ht_instance_asset(asset_name: str, name: str,
                      collection: bpy.types.Collection) -> bpy.types.Object | None:
    """Creates an object that shares the mesh of a catalog asset.

    Args:
        asset_name: Name of the catalog object, e.g. SM_ht_post_stone_40x260x40_01.
        name: Name of the new object.
        collection: Collection the new object is linked to.

    Returns:
        The new object, or None if the asset does not exist.
    """
    source: bpy.types.Object | None = bpy.data.objects.get(asset_name)
    if source is None:
        print(f"ht_instance_asset: asset '{asset_name}' not found")
        return None

    obj: bpy.types.Object = bpy.data.objects.new(name, source.data)
    collection.objects.link(obj)
    return obj


def _read_str_prop(obj: bpy.types.Object, key: str) -> str | None:
    """Reads a string custom property from the mesh of an object.

    Args:
        obj: Catalog object whose mesh holds the property.
        key: Property name, e.g. ht_kind.

    Returns:
        The string, or None (with a warning) if it is missing or not a string.
    """
    data: bpy.types.ID | None = obj.data
    if data is None:
        print(f"_read_str_prop: '{obj.name}' has no data")
        return None

    value: object = data.get(key)
    if value is None:
        print(f"_read_str_prop: '{obj.name}' has no property '{key}'")
        return None
    if not isinstance(value, str):
        print(f"_read_str_prop: '{obj.name}' property '{key}' is not a string")
        return None
    return value


def _parse_size_and_variant(name: str) -> tuple[int, int, int, int] | None:
    """Reads length, height, depth and variant from the last two name tokens.

    Args:
        name: Object name, e.g. SM_ht_wall_160x220x30_01.

    Returns:
        (length_cm, height_cm, depth_cm, variant), or None if the name does not fit.
    """
    tokens: list[str] = name.split("_")
    if len(tokens) < 2:
        return None

    try:
        variant: int = int(tokens[-1])
        length_cm, height_cm, depth_cm = (int(part) for part in tokens[-2].split("x"))
    except ValueError:
        return None
    return length_cm, height_cm, depth_cm, variant


def ht_discover_assets(collection_name: str) -> list[HtAssetDef]:
    """Builds asset definitions from the objects of a catalog collection.

    Args:
        collection_name: Name of the collection to scan.

    Returns:
        One definition per valid asset, invalid ones are skipped with a warning.
    """
    assets: list[HtAssetDef] = []
    collection: bpy.types.Collection | None = bpy.data.collections.get(collection_name)
    if collection is None:
        print(f"ht_discover_assets: collection '{collection_name}' not found")
        return assets

    for obj in collection.objects:
        # Foreign objects (cameras, lights, ...) are not ours, skip silently
        if not obj.name.startswith("SM_ht_"):
            continue

        kind_raw: str | None = _read_str_prop(obj, "ht_kind")
        material_raw: str | None = _read_str_prop(obj, "ht_material")
        layer_raw: str | None = _read_str_prop(obj, "ht_layer")
        if kind_raw is None or material_raw is None or layer_raw is None:
            continue

        kind: HtAssetKind | None = ht_parse_enum(HtAssetKind, kind_raw)
        if kind is None:
            print(f"ht_discover_assets: unknown kind '{kind_raw}' on '{obj.name}'")
            continue
        material: HtAssetMaterial | None = ht_parse_enum(HtAssetMaterial, material_raw)
        if material is None:
            print(f"ht_discover_assets: unknown material '{material_raw}' on '{obj.name}'")
            continue
        layer: HtAssetLayer | None = ht_parse_enum(HtAssetLayer, layer_raw)
        if layer is None:
            print(f"ht_discover_assets: unknown layer '{layer_raw}' on '{obj.name}'")
            continue

        parsed: tuple[int, int, int, int] | None = _parse_size_and_variant(obj.name)
        if parsed is None:
            print(f"ht_discover_assets: cannot read size/variant from '{obj.name}'")
            continue
        length_cm, height_cm, depth_cm, variant = parsed

        asset: HtAssetDef = HtAssetDef(
            name=obj.name,
            kind=kind,
            material=material,
            layer=layer,
            length_cm=length_cm,
            height_cm=height_cm,
            depth_cm=depth_cm,
            variant=variant,
        )
        assets.append(asset)
        print(f"ht_discover_assets: {asset}")

    return assets
