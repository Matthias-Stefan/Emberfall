// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "Emberfall/Gameplay/World/Cover/CoverGroup.h"

#include "CoreMinimal.h"

class ACoverObject;
class FCoverSpatialGrid;
class UCoverSettings;


/**
 * @brief Derives cover groups from a set of objects, using the spatial grid for candidate pairs.
 */
class EMBERFALL_API FCoverGrouper
{
public:
    /**
     * @brief Creates a grouper that reads candidate pairs from the grid and @c MergeRadius from the settings.
     * @param InGrid is the grid providing the candidate pairs, it must outlive the grouper.
     * @param InSettings is the settings object providing @c MergeRadius, it must outlive the grouper.
     */
    FCoverGrouper(const FCoverSpatialGrid& InGrid, const UCoverSettings& InSettings);

    /**
     * @brief Deleted, a grouper without grid and settings is not valid.
     */
    FCoverGrouper() = delete;

    /**
     * @brief Builds the groups so that every object ends up in exactly one group.
     * @param Objects is the list of all objects to group.
     * @param OutGroups is filled with the groups, previous content is discarded.
     */
    void Build(const TArray<ACoverObject*>& Objects, TArray<FCoverGroup>& OutGroups) const;

private:
    /** @brief Grid providing the candidate pairs, not owned. */
    const FCoverSpatialGrid& Grid;

    /** @brief Settings providing @c MergeRadius, not owned. */
    const UCoverSettings& Settings;
};