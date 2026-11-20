// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

#include "Emberfall/Core/Geometry/Polygon2D.h"
#include "Emberfall/Core/Geometry/Polyline2D.h"
#include "Emberfall/Gameplay/World/Cover/CoverTypes.h"


/**
 * @brief Cover-specific geometry helpers and the bridge from world-space corner lists to the generic 2D geometry classes.
 */
class EMBERFALL_API FCoverGeometry
{
public:
    /**
     * @brief Deleted, this class only provides static functions.
     */
    FCoverGeometry() = delete;

    /**
     * @brief Converts a list of world-space corners to a polygon in the ground plane, dropping Z.
     * @param Corners is the list of corners in world space in cm, in order.
     * @return Polygon with the X and Y of every corner.
     */
    [[nodiscard]] static FPolygon2D ToPolygon2D(const TArray<FVector>& Corners);

    /**
     * @brief Converts a list of world-space points to a polyline in the ground plane, dropping Z.
     * @param Points is the list of points in world space in cm, in order.
     * @param bIsClosed is whether the last point connects back to the first.
     * @return Polyline with the X and Y of every point.
     */
    [[nodiscard]] static FPolyline2D ToPolyline2D(const TArray<FVector>& Points, bool bIsClosed);

    /**
     * @brief Grows a convex footprint outward by a distance, keeping the corners sharp.
     * @param ConvexCorners is the list of the footprint corners in world space in cm, either winding order.
     * @param Offset is the distance each edge is pushed outward in cm.
     * @param MiterLimit is the maximum corner shift as a multiple of @c Offset.
     * @param OutCorners is filled with the grown corners in world space in cm, counterclockwise, each at the height of its source corner.
     * @return @c true if the footprint was grown, @c false if there are fewer than three corners or a corner spikes.
     */
    static bool BuildGrownCorners(const TArray<FVector>& ConvexCorners, double Offset, double MiterLimit,
        TArray<FVector>& OutCorners);

    /**
     * @brief Determines which local side of a wall an edge piece lies on.
     * @param OutwardNormal is the normalized normal of the piece pointing out of its footprint.
     * @param AxisX is the world direction of the local positive X axis of the wall.
     * @param AxisY is the world direction of the local positive Y axis of the wall.
     * @return The side whose axis is closest to @c OutwardNormal.
     */
    static ECoverSide ClassifySide2D(const FVector2D& OutwardNormal, const FVector2D& AxisX, const FVector2D& AxisY);
};
