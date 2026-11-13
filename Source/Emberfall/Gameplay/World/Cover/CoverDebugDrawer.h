// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

#if ENABLE_DRAW_DEBUG

#include "Emberfall/Gameplay/World/Cover/CoverGroup.h"
#include "Emberfall/Gameplay/World/Cover/CoverTypes.h"

class FCoverSpatialGrid;
class UCoverSettings;
class UWorld;


/**
 * @brief Draws debug visuals for the cover system, read-only and without own data.
 */
class EMBERFALL_API FCoverDebugDrawer
{
public:
    /**
     * @brief Creates a drawer for one world.
     * @param InWorld is the world to draw into, it must outlive the drawer.
     * @param InSettings is the settings object providing the debug offsets, it must outlive the drawer.
     */
    FCoverDebugDrawer(const UWorld& InWorld, const UCoverSettings& InSettings);

    /**
     * @brief Deleted, a drawer without world and settings is not valid.
     */
    FCoverDebugDrawer() = delete;

    /**
     * @brief Draws every occupied grid cell as a flat box with a label.
     * @param Grid is the grid to visualize.
     * @param Duration is the lifetime of the shapes in seconds, @c -1 keeps them until the world ends.
     */
    void DrawCells(const FCoverSpatialGrid& Grid, float Duration) const;

    /**
     * @brief Draws the footprints of all group members, one blue tone per group, plus a label per group.
     * @param Groups is the list of groups to visualize.
     * @param Duration is the lifetime of the shapes in seconds, @c -1 keeps them until the world ends.
     */
    void DrawGroups(const TArray<FCoverGroup>& Groups, float Duration) const;

    /**
     * @brief Draws every footprint edge of all group members, enabled sides in green and disabled sides in red.
     * @param Groups is the list of groups whose members are drawn.
     * @param Duration is the lifetime of the lines in seconds, @c -1 keeps them until the world ends.
     */
    void DrawEnabledSides(const TArray<FCoverGroup>& Groups, float Duration) const;

    /**
     * @brief Draws every loop with numbered points, one color per loop, closed loops get a closing line.
     * @param Loops is the list of loops to visualize.
     * @param Duration is the lifetime of the shapes in seconds, @c -1 keeps them until the world ends.
     */
    void DrawLoops(const TArray<FCoverLoop>& Loops, float Duration) const;

    /**
     * @brief Draws the four footprint edges of one wall, enabled sides in green and disabled sides in red.
     * @param CoverObject is the wall to draw.
     * @param Duration is the lifetime of the lines in seconds, @c 0 draws for one frame only, @c -1 keeps them until the world ends.
     */
    void DrawSides(const ACoverObject& CoverObject, float Duration) const;
    
private:
    /**
     * @brief Derives a stable blue tone from a group id.
     * @param GroupId is the identifier of the group.
     * @return Color that differs in hue and brightness between neighboring ids.
     */
    static FColor GetGroupColor(int32 GroupId);

    /**
     * @brief Derives a stable color from a loop index.
     * @param LoopIndex is the position of the loop in its list.
     * @return Bright color that differs in hue between neighboring indices.
     */
    static FColor GetLoopColor(int32 LoopIndex);

    /** @brief World to draw into, not owned. */
    const UWorld& World;

    /** @brief Settings providing the debug offsets, not owned. */
    const UCoverSettings& Settings;
};

#endif