// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

class UCoverSettings;
class ACoverObject;


/**
 * @brief Sparse spatial hash that maps grid cells to the cover objects touching them.
 */
class EMBERFALL_API FCoverSpatialGrid
{
public:
    /**
     * @brief Creates a grid that reads its dimensions from the given settings.
     * @param InSettings is the settings object providing @c CellSize and @c MergeRadius, it must outlive the grid.
     */
    explicit FCoverSpatialGrid(const UCoverSettings& InSettings);

    /**
     * @brief Deleted, a grid without settings is not valid.
     */
    FCoverSpatialGrid() = delete;

    /**
     * @brief Inserts a cover object into all cells its expanded footprint touches.
     * @param CoverObject is the object to insert.
     * @return @c true if inserted, @c false if invalid, already inserted or without footprint.
     */
    [[nodiscard]] bool Insert(ACoverObject* CoverObject);

    /**
     * @brief Removes a cover object from all cells it was inserted into.
     * @param CoverObject is the object to remove.
     * @return @c true if it was in the grid, otherwise @c false.
     */
    bool Remove(ACoverObject* CoverObject);

    /**
     * @brief Collects the candidates in all cells touched by the query square.
     * @param Position is the center of the query square in world space.
     * @param Radius is the half edge length of the query square in cm.
     * @param OutCoverObjects is filled with each found object once.
     */
    void Query(const FVector& Position, float Radius, TArray<ACoverObject*>& OutCoverObjects) const;

    /**
     * @brief Collects all pairs of objects that share at least one cell.
     * @param OutPairs is filled with each pair once, regardless of how many cells it shares.
     */
    void GetCandidatePairs(TArray<TPair<ACoverObject*, ACoverObject*>>& OutPairs) const;

    /**
     * @brief Removes all objects and cells.
     */
    void Empty();

    /**
     * @brief Gives read access to the occupied cells, e.g. for debug drawing.
     * @return Map from cell to the objects touching it.
     */
    const TMap<FIntPoint, TArray<TWeakObjectPtr<ACoverObject>>>& GetCells() const { return Cells; }

    /**
     * @brief Gets the cell size currently used by the grid.
     * @return Cell edge length in cm, at least @c 1.
     */
    float GetCellSize() const;

private:
    /**
     * @brief Maps a world position to its grid cell.
     * @param WorldPosition is the position in world space.
     * @return The cell containing @c WorldPosition.
     */
    FIntPoint WorldToCell(const FVector& WorldPosition) const;

    /**
     * @brief Computes all cells touched by a footprint, expanded by @c MergeRadius.
     * @param CoverObject is the object to measure.
     * @param OutCells is filled with the touched cells.
     * @return @c true if the cells were computed, @c false if the object has no footprint.
     */
    bool ComputeOccupiedCells(const ACoverObject& CoverObject, TArray<FIntPoint>& OutCells) const;

    /**
     * @brief Gets the footprint expansion currently used by the grid.
     * @return Expansion in cm, at least @c 0.
     */
    float GetMergeRadius() const;

    /** @brief Settings providing @c CellSize and @c MergeRadius, not owned. */
    const UCoverSettings& Settings;

    /** @brief Sparse map from a cell to the objects touching it. */
    TMap<FIntPoint, TArray<TWeakObjectPtr<ACoverObject>>> Cells;

    /** @brief Cells each object was inserted into, needed for removal. */
    TMap<TWeakObjectPtr<ACoverObject>, TArray<FIntPoint>> OccupiedCells;
};