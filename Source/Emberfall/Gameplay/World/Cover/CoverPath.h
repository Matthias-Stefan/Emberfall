// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "CoverPath.generated.h"

class ACoverObject;


/**
 * @brief One wall inside a @c UCoverPath.
 */
struct FCoverPathSegment
{
    /** @brief The wall of this segment; owned by the level. */
    TWeakObjectPtr<ACoverObject> Wall{};
    
    /** @brief Distance in cm along the path where this wall begins. */
    float StartDistance{ 0.0f };
    
    /** @brief Length of this segment in cm. */
    float Length{ 0.0f };

    /** @brief World-space point where the segment begins, in path direction. */
    FVector From{ FVector::ZeroVector };

    /** @brief World-space point where the segment ends, in path direction. */
    FVector To{ FVector::ZeroVector };

    /** @brief Dock normal of the wall, pointing away from the wall. */
    FVector Normal{ FVector::ZeroVector };
};


/**
 * @brief Run of connected cover walls that units move along as one continuous path.
 */
UCLASS()
class EMBERFALL_API UCoverPath : public UObject
{
    GENERATED_BODY()

public:
    /**
     * @brief Builds the segments from the walls and measures the path.
     * @param OrderedWalls Walls of the path, ordered from one end to the other.
     */
    void Initialize(const TArray<TWeakObjectPtr<ACoverObject>>& OrderedWalls);

    /**
     * @brief Returns the total length of the path.
     * @return Length in cm.
     */
    float GetLength() const { return Length; }

    /**
     * @brief Finds the point of the path closest to a world location.
     * @param WorldLocation Location to project onto the path.
     * @return Distance in cm along the path.
     */
    float FindDistanceClosestTo(const FVector& WorldLocation) const;

    /**
     * @brief Returns the world location at a distance along the path.
     * @param Distance Distance in cm, clamped to @c 0 .. @c Length.
     * @return World location on the cover line.
     */
    FVector GetLocationAtDistance(float Distance) const;

    /**
     * @brief Returns the dock normal of the wall at a distance along the path.
     * @param Distance Distance in cm, clamped to @c 0 .. @c Length.
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
    
private:
    /** @brief Walls of the path in order, with their position on the path. */
    TArray<FCoverPathSegment> Segments{};

    /** @brief Total length of the path in cm. */
    float Length{ 0.0f };
};