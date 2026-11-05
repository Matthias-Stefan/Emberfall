---
type: system
status: in-progress
category: gameplay
topics: [cover]
tags: [emberfall]
author: matthias stefan
date-added: 2026-11-02
date-completed:
---

# Cover System

> Turns separate wall modules into one continuous cover path the player character walks along.

The game world is built from wall modules. Placed next to each other, they form corners, T-junctions and rooms.
Instead of treating every wall on its own, the cover system merges touching walls into one group and generates a
single path around it.

The player character is locked onto this path. Moving along it, the player can peek around corners to spot enemies
without leaving cover.

![cover-path-overview.png|700](Assets/cover-path-overview.svg)

___
## 1. `ACoverObject` and Footprint

The cover system works on `ACoverObject`, an actor derived from `AActor`. It owns a `UStaticMeshComponent` as its root, and the bounds of the assigned static mesh are the only thing the system reads from it. From these bounds, the object computes its **footprint**: four corners on the ground, rotated and scaled with the actor (an oriented bounding box, not an axis-aligned one).


![[cover-footprint.svg|1400]]

When an `ACoverObject` is constructed, `OnConstruction` calls `BuildPerimeter()`, which in turn calls `GetFootprintCorners()`. The footprint is the foundation for everything that follows: the spatial grid, the grouping and the cover paths are all built from it.

### How `GetFootprintCorners` works

1. **Read the bounds in mesh space.** `Mesh->GetBounds()` returns the unrotated box of the mesh as `Origin` and
   `BoxExtent`.
2. **Derive the ground rectangle.** `HalfX` and `HalfY` are the extents on X and Y times `ExtentScale`. The corners lie
   on the bottom of the box, at `BottomZ = Origin.Z - BoxExtent.Z`.
3. **Build the four corners** at `Origin ± (HalfX, HalfY)`, always in the same order.
4. **Transform them into world space** with the component transform. Rotation, scale and position of the actor move
   all four corners, so the result is an oriented box instead of an axis-aligned one.

The function returns `false` if no static mesh is assigned. The mesh needs no collision, because the bounds come from
the mesh itself and not from the physics shapes.

## 2. Registry and spatial grid







## A. Open

### Outline
- [x] Chain the kept pieces into ordered, closed loops (tolerance on end points)
- [x] Simplify loops (Ramer-Douglas-Peucker) and drop tiny loops
- [x] Store the loops in `FCoverGroup`
- [x] Move the loop building from `DrawDebug` into `FCoverOutlineBuilder` (`Build`, `BuildGrownFootprints`)
- [x] `ensure` that `OutlineOffset >= MergeRadius / 2`
- [x] Decided: closed loop around the group first, path on selected sides later
- [ ] Tell outer loops from holes (courtyards), e.g. by winding
- [ ] Per-wall side selection: pieces carry their source loop and edge, abandoned sides are dropped before chaining
- [ ] Known gap: two shapes that only touch with opposite edges keep an edge in their interior
- [ ] Set the default of `OutlineSimplifyTolerance` to 15 cm, matching the tested value

### Cover system
- [x] Self-registration in `ACoverObject` (`BeginPlay` / `EndPlay`)
- [x] Dirty flag for groups, rebuild once per frame instead of only at world start
- [ ] First unit that uses the outline (nearest point, walk along, lock onto the path)
- [ ] Replace or remove the per-object `PerimeterSpline`, `PerimeterHeight` and `PerimeterScale`
- [ ] Optional: cache outlines by member set (mage wall)

### Cleanup
- [ ] Doxygen for the new geometry functions, `FCoverEdgePiece`, `FCoverLoop` and `FCoverOutlineBuilder`
- [x] `Num() < 3` guard in `ContainsPoint2D`
- [ ] Automation tests for `FCoverGeometry` and `FDisjointSet`
- [ ] Note the simplification: height is ignored, all cover stands on one level

### Documentation
- [x] Section 1: `ACoverObject` and footprint
- [ ] Section 2: registry and spatial grid
- [ ] Section 3: groups
- [ ] Section 4: outline (picture series with the L example)
- [ ] Section 5: settings table


## B. Future checks
- [ ] Rebuild only the affected groups (needs stable group ids and an object to group lookup), only if `RebuildGroups` shows up in profiling
