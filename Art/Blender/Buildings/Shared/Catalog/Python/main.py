# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Entry script: rebuilds the generated module catalog and house grid in Blender."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

# Run in the Blender console:
# exec(bpy.data.texts["main.py"].as_string())

import sys
from pathlib import Path

import bpy

GEN_MODULES_COLLECTION: str = "GenModules"
GEN_HOUSES_COLLECTION: str = "GenHouses"
PACKAGE_PREFIXES: tuple[str, ...] = ("bld_",)


def setup_python_path() -> None:
    """Adds the Python folder next to the .blend file to sys.path."""
    python_dir: Path = Path(bpy.path.abspath("//")) / "Python"
    if str(python_dir) not in sys.path:
        sys.path.append(str(python_dir))


def unload_packages() -> None:
    """Drops cached package modules so edits are picked up on re-run."""
    for module_name in list(sys.modules):
        if module_name.startswith(PACKAGE_PREFIXES):
            del sys.modules[module_name]


def recreate_collection(name: str) -> bpy.types.Collection:
    """Deletes the named collection with all its content and creates it anew.

    Args:
        name: Collection name.

    Returns:
        The fresh, empty collection linked to the scene root.
    """
    existing: bpy.types.Collection | None = bpy.data.collections.get(name)
    if existing is not None:
        for stale_object in list(existing.all_objects):
            stale_data: bpy.types.ID | None = stale_object.data
            bpy.data.objects.remove(stale_object, do_unlink=True)
            if isinstance(stale_data, bpy.types.Mesh) and stale_data.users == 0:
                bpy.data.meshes.remove(stale_data)
        bpy.data.collections.remove(existing)

    collection: bpy.types.Collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def setup_viewport_color() -> None:
    """Switches the 3D viewports of every workspace to solid shading with object colors."""
    for screen in bpy.data.screens:
        for screen_area in screen.areas:
            if screen_area.type != "VIEW_3D":
                continue
            for space in screen_area.spaces:
                if space.type == "VIEW_3D":
                    space.shading.type = "SOLID"
                    space.shading.color_type = "OBJECT"


def main() -> None:
    """Rebuilds everything generated from scratch."""
    setup_python_path()
    unload_packages()

    # imported here, the packages are only found after the path setup and a fresh unload
    from bld_testbed import TestbedRunner

    modules_collection: bpy.types.Collection = recreate_collection(GEN_MODULES_COLLECTION)
    houses_collection: bpy.types.Collection = recreate_collection(GEN_HOUSES_COLLECTION)
    TestbedRunner(modules_collection, houses_collection).run()
    setup_viewport_color()


if __name__ == "__main__":
    main()
