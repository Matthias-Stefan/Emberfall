// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "Emberfall/Gameplay/World/Cover/CoverSettings.h"

class FCoverGroup;
struct FCoverEdgePiece;
struct FCoverGrownFootprint;
struct FCoverLoop;


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
     * @brief Cuts the border of every grown footprint at its crossings with the others and keeps the pieces on the outer boundary.
     * @param Footprints is the list of grown footprints, all with the same winding.
     * @param OutPieces is filled with the kept pieces, each carrying the index of its footprint, previous content is discarded.
     */
    void FilterOuterPieces(const TArray<FCoverGrownFootprint>& Footprints, TArray<FCoverEdgePiece>& OutPieces) const;

    /**
     * @brief Chains edge pieces into ordered closed loops by matching end points to start points.
     * @param Pieces is the list of edge pieces, all running in the same direction.
     * @param OutLoops is filled with one loop per chain, previous content is discarded.
     */
    void ChainPieces(const TArray<FCoverEdgePiece>& Pieces, TArray<FCoverLoop>& OutLoops) const;
    
    /**
     * @brief Grows the footprint of every member of a group by the outline offset and copies the side data of the wall.
     * @param Group is the group whose members are grown.
     * @param OutFootprints is filled with one grown footprint per valid member, previous content is discarded.
     */
    void BuildGrownFootprints(const FCoverGroup& Group, TArray<FCoverGrownFootprint>& OutFootprints) const;
    
private:
    /**
     * @brief Decides whether a piece of one footprint lies on the outer boundary of all footprints.
     * @param Footprints is the list of all grown footprints.
     * @param OwnFootprintIndex is the index of the footprint the piece belongs to.
     * @param OutwardNormal is the normalized normal of the piece pointing out of its footprint.
     * @param MidPoint is the midpoint of the piece.
     * @return @c true if the piece stays, @c false if it lies inside another footprint or duplicates a piece that a lower footprint keeps.
     */
    bool IsPieceOuter(const TArray<FCoverGrownFootprint>& Footprints, int32 OwnFootprintIndex,
        const FVector2D& OutwardNormal, const FVector& MidPoint) const;

    /**
     * @brief Removes points of a closed loop that deviate less than the simplify tolerance from the simplified line.
     * @param Loop is the loop to simplify.
     * @param OutLoop is filled with the simplified loop, previous content is discarded.
     */
    void SimplifyLoop(const FCoverLoop& Loop, FCoverLoop& OutLoop) const;
    
    /** @brief Settings providing @c OutlineBorderTolerance, not owned. */
    const UCoverSettings& Settings;
};
