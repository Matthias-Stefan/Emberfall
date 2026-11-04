// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "Emberfall/Gameplay/World/Cover/CoverSettings.h"

class FCoverGroup;
struct FCoverLoop;
struct FCoverEdgePiece;


class FCoverOutlineBuilder
{
public:
    /**
     * @brief Creates a builder that reads the border tolerance from the settings.
     * @param InSettings is the settings object providing @c OutlineBorderTolerance, it must outlive the builder.
     */
    explicit FCoverOutlineBuilder(const UCoverSettings& InSettings);

    FCoverOutlineBuilder() = delete;

    /**
     * @brief Builds the closed outline loops around all members of a group.
     * @param Group is the group to build the outline for.
     * @param OutLoops is filled with one loop per outer boundary, previous content is discarded.
     */
    void Build(const FCoverGroup& Group, TArray<FCoverLoop>& OutLoops) const;
    
    /**
     * @brief Cuts every loop at its crossings with the other loops and keeps the pieces on the outer boundary.
     * @param Loops is the list of closed convex loops, all with the same winding.
     * @param OutPieces is filled with the kept pieces, previous content is discarded.
     */
    void FilterOuterPieces(const TArray<TArray<FVector>>& Loops, TArray<FCoverEdgePiece>& OutPieces) const;

    /**
     * @brief Chains edge pieces into ordered closed loops by matching end points to start points.
     * @param Pieces is the list of edge pieces, all running in the same direction.
     * @param OutLoops is filled with one loop per chain, previous content is discarded.
     */
    void ChainPieces(const TArray<FCoverEdgePiece>& Pieces, TArray<FCoverLoop>& OutLoops) const;
    
    /**
     * @brief Grows the footprint of every member of a group by the outline offset.
     * @param Group is the group whose members are grown.
     * @param OutFootprints is filled with one grown footprint per valid member, previous content is discarded.
     */
    void BuildGrownFootprints(const FCoverGroup& Group, TArray<TArray<FVector>>& OutFootprints) const;
    
private:
    /**
     * @brief Decides whether a piece of one loop lies on the outer boundary of all loops.
     * @param Loops is the list of all loops.
     * @param OwnLoopIndex is the index of the loop the piece belongs to.
     * @param MidPoint is the midpoint of the piece.
     * @return @c true if the piece stays, @c false if it lies inside another loop or duplicates a piece of a lower loop.
     */
    bool IsPieceOuter(const TArray<TArray<FVector>>& Loops, int32 OwnLoopIndex, const FVector& MidPoint) const;

    /** @brief Settings providing @c OutlineBorderTolerance, not owned. */
    const UCoverSettings& Settings;
};
