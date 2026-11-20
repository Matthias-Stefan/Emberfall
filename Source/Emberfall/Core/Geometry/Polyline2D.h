// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "Emberfall/Core/Geometry/Segment2D.h"

#include "CoreMinimal.h"


/**
 * @brief Open or closed path through a list of points in the ground plane.
 */
class FPolyline2D
{
public:
    /**
     * @brief Creates a polyline from its points.
     * @param InPoints is the list of points in cm.
     * @param bInIsClosed is whether the last point connects back to the first.
     */
    FPolyline2D(TArray<FVector2D> InPoints, bool bInIsClosed)
        : Points(MoveTemp(InPoints))
          , bIsClosed(bInIsClosed)
    {
    }

    //~=============================================================================
    // Validity

    /** @brief Open polyline without points that marks the absence of a polyline. */
    static const FPolyline2D Invalid;

    /**
     * @brief Tests whether the polyline has at least one segment.
     * @return @c true if there are at least two points, otherwise @c false.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT bool IsValid() const { return GetSegmentNum() > 0; }

    //~=============================================================================
    // Access

    /**
     * @brief Tests whether the last point connects back to the first.
     * @return @c true if the polyline is closed, otherwise @c false.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT bool IsClosed() const { return bIsClosed; }

    /**
     * @brief Gets the number of points.
     * @return Point count.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT int32 GetPointNum() const { return Points.Num(); }

    /**
     * @brief Gets the number of segments between the points.
     * @return Segment count, one less than the point count if open, @c 0 if there are fewer than two points.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT int32 GetSegmentNum() const
    {
        if (GetPointNum() < 2)
        {
            return 0;
        }

        const int32 SegmentNum = bIsClosed ? GetPointNum() : GetPointNum() - 1;
        return SegmentNum;
    }

    /**
     * @brief Gets a segment from a point to the next point.
     * @param Index is the index of the point the segment starts at.
     * @return Segment, the last segment of a closed polyline ends at the first point.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT FSegment2D GetSegment(int32 Index) const
    {
        checkf(Index >= 0 && Index < GetSegmentNum(), TEXT("Segment index %d is out of range."), Index);
        const FVector2D Start = Points[Index];
        const FVector2D End = Points[NextIndex(Index)];
        return FSegment2D(Start, End);
    }

    //~=============================================================================
    // Shape

    /**
     * @brief Computes the length of the whole path.
     * @return Length in cm, @c 0 if there are fewer than two points.
     */
    [[nodiscard]] double GetLength() const;

    //~=============================================================================
    // Path queries

    /**
     * @brief Computes the point at a distance along the path, measured from the first point.
     * @param Distance is the distance along the path in cm.
     * @return Point on the path in cm, clamped to the ends if open, wrapped around if closed, the first point if the path has no length.
     */
    [[nodiscard]] FVector2D GetPointAtDistance(double Distance) const;

    /**
     * @brief Finds the point on the path that is closest to a position.
     * @param Point is the position to measure from.
     * @param OutDistanceAlong is filled with the distance of the found point along the path in cm, measured from the first point.
     * @return Closest point on the path in cm, @c ZeroVector if the polyline has no points.
     */
    [[nodiscard]] FVector2D FindClosestPoint(const FVector2D& Point, double& OutDistanceAlong) const;

private:
    /**
     * @brief Computes the index of the following point, wrapping around at the end.
     * @param Index is the index of the current point.
     * @return Index of the next point.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT int32 NextIndex(int32 Index) const
    {
        return Index + 1 == Points.Num() ? 0 : Index + 1;
    }

    /** @brief Points in order in cm. */
    TArray<FVector2D> Points;

    /** @brief Whether the last point connects back to the first. */
    bool bIsClosed = false;
};
