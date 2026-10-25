// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "CoverPath.generated.h"

struct FCoverRun;


/**
 * @brief One straight edge inside a @c UCoverPath.
 */
struct FCoverPathSegment
{
    /** @brief Distance in cm along the path where this segment begins. */
    float StartDistance{ 0.0f };

    /** @brief Length of this segment in cm. */
    float Length{ 0.0f };

    /** @brief World-space point where the segment begins, in path direction. */
    FVector From{ FVector::ZeroVector };

    /** @brief World-space point where the segment ends, in path direction. */
    FVector To{ FVector::ZeroVector };

    /** @brief Outward normal of the edge, pointing away from the wall. */
    FVector Normal{ FVector::ZeroVector };
};


/**
 * @brief Walkable run of a cover object that units move along as one continuous path.
 */
UCLASS()
class EMBERFALL_API UCoverPath : public UObject
{
    GENERATED_BODY()

public:
    /**
     * @brief Builds the segments from a run and measures the path.
     * @param Run Points, edge normals and the closed flag of the run.
     */
    void Initialize(const FCoverRun& Run);

    /**
     * @brief Returns the total length of the path.
     * @return Length in cm.
     */
    float GetLength() const { return Length; }

    /**
     * @brief Returns whether the path is a loop.
     * @return @c true if distances wrap around at @c Length.
     */
    bool IsClosed() const { return bClosed; }

    /**
     * @brief Finds the point of the path closest to a world location.
     * @param WorldLocation Location to project onto the path.
     * @return Distance in cm along the path.
     */
    float FindDistanceClosestTo(const FVector& WorldLocation) const;

    /**
     * @brief Returns the world location at a distance along the path.
     * @param Distance Distance in cm; wraps on closed paths, otherwise clamped to @c 0 .. @c Length.
     * @return World location on the path.
     */
    FVector GetLocationAtDistance(float Distance) const;

    /**
     * @brief Returns the normal of the edge at a distance along the path.
     * @param Distance Distance in cm; wraps on closed paths, otherwise clamped to @c 0 .. @c Length.
     * @return World-space normal pointing away from the wall.
     */
    FVector GetNormalAtDistance(float Distance) const;

private:
    /**
     * @brief Finds the segment that holds a distance along the path.
     * @param Distance Distance in cm along the path; values outside the path give the first or last segment.
     * @return The segment, or @c nullptr if the path is empty. Only valid until the next @c Initialize.
     */
    const FCoverPathSegment* GetSegmentAtDistance(float Distance) const;

    /**
     * @brief Wraps a distance into @c 0 .. @c Length on closed paths.
     * @param Distance Distance in cm along the path.
     * @return Wrapped distance for closed paths, @c Distance unchanged for open ones.
     */
    float WrapDistance(float Distance) const;

private:
    /** @brief Edges of the path in order, with their position on the path. */
    TArray<FCoverPathSegment> Segments{};

    /** @brief Total length of the path in cm. */
    float Length{ 0.0f };

    /** @brief Path is a loop; distances wrap around. */
    bool bClosed{ false };
};