// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "Emberfall/Core/Geometry/Polyline2D.h"

#include "CoreMinimal.h"


/**
 * @brief Stretches of a cover path a unit may walk on, separated by the corners and path ends it has to stop in front of.
 */
class FCoverPathSpans
{
public:
    /**
     * @brief Creates spans without limits, the unit may walk the whole path.
     */
    FCoverPathSpans() = default;

    /**
     * @brief Builds the spans of a cover path.
     * @param Path is the cover path in the ground plane.
     * @param bOutwardIsRightNormal is whether the right normal of the path segments points away from the wall.
     * @param MinCornerAngleDegrees is the smallest turn of the path at a point that counts as a corner in degrees.
     * @param CornerMargin is the distance in front of a corner or path end at which the unit stops in cm.
     * @return Spans, without limits if the path is closed and has no corner.
     */
    [[nodiscard]] static FCoverPathSpans Build(const FPolyline2D& Path, bool bOutwardIsRightNormal,
        double MinCornerAngleDegrees, double CornerMargin);

    /**
     * @brief Finds the walkable position closest to a distance along the path.
     * @param Distance is the distance along the path in cm.
     * @return Distance of the closest walkable position in cm, may lie outside of the path length on a closed path, @p Distance itself if there are no limits.
     */
    [[nodiscard]] double FindNearestFreeDistance(double Distance) const;

    /**
     * @brief Computes how far a unit may walk toward a target without passing a corner.
     * @param CurrentDistance is the position of the unit along the path in cm.
     * @param TargetDistance is the requested position along the path in cm.
     * @return Signed distance in cm, positive runs toward the end of the path, @c 0 if the unit stands in no span.
     */
    [[nodiscard]] double ComputeWalkDelta(double CurrentDistance, double TargetDistance) const;

private:
    /**
     * @brief Walkable range between two corners, measured along the path.
     */
    struct FSpan
    {
        /** @brief Start of the range in cm. */
        double Start = 0.0;

        /** @brief End of the range in cm, may exceed the path length on a closed path. */
        double End = 0.0;

        /**
         * @brief Computes how far a distance lies from the range.
         * @param Distance is the distance along the path in cm.
         * @return Gap in cm, @c 0 if the distance lies inside the range.
         */
        [[nodiscard]] double GetGap(double Distance) const
        {
            if (Distance < Start)
            {
                return Start - Distance;
            }

            return Distance > End ? Distance - End : 0.0;
        }
    };

    /**
     * @brief Tests whether the path turns at a point in a way that exposes the unit.
     * @param IncomingSegment is the segment that ends at the point.
     * @param OutgoingSegment is the segment that starts at the point.
     * @param bOutwardIsRightNormal is whether the right normal of the path segments points away from the wall.
     * @param MinCornerAngleDegrees is the smallest turn that counts as a corner in degrees.
     * @return @c true if the turn is at least @p MinCornerAngleDegrees and leads toward the wall, otherwise @c false.
     */
    [[nodiscard]] static bool IsBlockingCorner(const FSegment2D& IncomingSegment, const FSegment2D& OutgoingSegment,
        bool bOutwardIsRightNormal, double MinCornerAngleDegrees);

    /** @brief Walkable ranges in path order, empty if the unit may walk the whole path. */
    TArray<FSpan> Spans;

    /** @brief Length of the path in cm. */
    double PathLength = 0.0;

    /** @brief Whether the path is closed, so distances wrap around at the path length. */
    bool bIsClosed = false;
};
