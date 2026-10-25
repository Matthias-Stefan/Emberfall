# Cover System TODO

| #  | Topic                     | Problem / Goal                                                                                                                      | Depends on |
|----|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------|------------|
| 1  | Own path movement        | Replace `MoveToLocation`; the component advances the distance itself and `GetSignedCoverSpeed` comes from it. Needed to walk around corners. | -          |
| 2  | Side change transition   | Switching the wall side (e.g. `NegativeY` -> `PositiveY`) needs a transition (slide/animation). The unit must not stand in the air at the wall end. | 1          |
| 3  | Normal blend at corners  | Rotation snaps at edge borders; blend the normal over +-30 cm. Facing still looks wrong, check `bUseControllerRotationYaw` (store the original value instead of resetting to `true`). | 1          |
| 4  | X sides (short ends)     | Hiding along X rarely makes sense, but thick walls may need it. Keep as `ActiveSides` option, decide the default per object.        | -          |
| 5  | Outer corners, round     | Outer corner handling and arc segments for rounded corners.                                                                         | 1, 3       |
| 6  | T, L and round shapes    | Outline is fixed to 4 points / 4 `ECoverSide` bits. Needs N points and a per-edge active mask (or `TArray<bool>`) instead of the 4-bit bitmask. | 5          |
| 7  | Height per side          | Low on one side, high on the other; `CoverHeight` moves from object to edge.                                                        | 6          |
| 8  | Chains across objects    | Re-introduce wall chains over several obstacles if needed.                                                                          | 6          |
| 9  | Units during path rebuild | `UCoverComponent` keeps the old path after `ActiveSidesChanged`; bind to the delegate and re-dock or leave cover. Old paths pile up in `Paths`. | -          |
| 10 | Runtime spawned objects  | `UCoverSubsystem` only collects objects in `OnWorldBeginPlay`; add an actor-spawned handler.                                        | -          |
| 11 | Debug draw               | Tick + `ShouldTickIfViewportsOnly` only for debugging; guard with `!UE_BUILD_SHIPPING` or remove.                                    | -          |
| 12 | Temp input               | C/V keys in `AEmberfallPlayerController` -> `IA_ToggleCover` / `IA_LeaveCover`.                                                     | -          |
| 13 | Build.cs cleanup         | `"WaveTable"` plus the `PrivateDependencyModuleNames` block can go (source of the "uproject does not list plugin" warning).         | -          |