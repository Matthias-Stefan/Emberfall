// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "Emberfall/Core/Geometry/Segment2D.h"

#include "CoreMinimal.h"



/**
 * @brief Closed polygon in the ground plane, defined by its corner points in order.
 */
class FPolygon2D
{
public:
    /**
     * @brief Creates a polygon from its corner points.
     * @param InPoints is the list of corners in cm, the last corner connects back to the first.
     */
    explicit FPolygon2D(TArray<FVector2D> InPoints)
        : Points(MoveTemp(InPoints))
    {
    }

    //~=============================================================================
    // Validity
    
    /** @brief Polygon without corners that marks the absence of a polygon. */
    static const FPolygon2D Invalid;
    
    /**
     * @brief Tests whether the polygon has enough corners to enclose an area.
     * @return @c true if there are at least three corners, otherwise @c false.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT bool IsValid() const { return GetPointNum() >= 3; }
    
    //~=============================================================================
    // Access

    /**
     * @brief Gets the number of corners, which equals the number of segments.
     * @return Corner count.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT int32 GetPointNum() const { return Points.Num(); }

    /**
     * @brief Gets a corner point.
     * @param Index is the index of the corner.
     * @return Corner in cm.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT const FVector2D& GetPoint(int32 Index) const
    {
        checkf(Points.IsValidIndex(Index), TEXT("Point index %d is out of range."), Index);
        return Points[Index];
    }

    /**
     * @brief Gets an segment from a corner to the next corner.
     * @param Index is the index of the corner the segment starts at.
     * @return Edge segment, the last segment ends at the first corner.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT FSegment2D GetSegment(int32 Index) const
    {
        checkf(Points.IsValidIndex(Index), TEXT("Segment index %d is out of range."), Index);
        const FVector2D Start = Points[Index];
        const FVector2D End = Points[NextIndex(Index)];
        return FSegment2D(Start, End);
    }

    //~=============================================================================
    // Shape

    /**
     * @brief Computes the signed area of the polygon with the shoelace formula.
     * @return Area in cm², positive if the corners run counterclockwise (X towards Y), negative if clockwise, @c 0 if there are fewer than three corners.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT double GetSignedArea() const;

    /**
     * @brief Computes the area of the polygon.
     * @return Area in cm², @c 0 if there are fewer than three corners.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT double GetArea() const
    {
        const double Area = FMath::Abs(GetSignedArea());
        return Area;
    }

    /**
     * @brief Computes the length of the border.
     * @return Perimeter in cm, @c 0 if the polygon has no corners.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT double GetPerimeter() const;

    /**
     * @brief Computes the area centroid of the polygon.
     * @return Centroid in cm, the average of the corners if the area is practically @c 0, @c ZeroVector if there are no corners.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT FVector2D GetCentroid() const;

    /**
     * @brief Tests whether the corners run counterclockwise (X towards Y).
     * @return @c true if the signed area is positive, otherwise @c false.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT bool IsCounterClockwise() const
    {
        const bool bIsCounterClockwise = GetSignedArea() > 0.0;
        return bIsCounterClockwise;
    }

    /**
     * @brief Builds a polygon whose segments are moved along their outward normals, with sharp corners.
     * @param Distance is the distance every segment is moved in cm, positive grows the polygon, negative shrinks it.
     * @return Offset polygon, a copy of this polygon if it has fewer than three corners.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT FPolygon2D BuildOffset(double Distance) const;
    
    /**
     * @brief Tests whether a simple polygon is convex.
     * @return @c true if all corners turn in the same direction, otherwise @c false.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT bool IsConvex() const;

    /**
     * @brief Computes the normalized normal of a segment pointing out of the polygon.
     * @param Index is the index of the corner the segment starts at.
     * @return Unit normal, @c ZeroVector if the segment is degenerate.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT FVector2D GetSegmentOutwardNormal(int32 Index) const
    {
        const FVector2D RightNormal = GetSegment(Index).GetRightNormal();
        const FVector2D OutwardNormal = IsCounterClockwise() ? RightNormal : -RightNormal;
        return OutwardNormal;
    }

    //~=============================================================================
    // Containment

    /**
     * @brief Tests whether a position lies inside the polygon.
     * @param Point is the position to test.
     * @return @c true if @c Point is inside, otherwise @c false, positions exactly on the border may go either way.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT bool ContainsPoint(const FVector2D& Point) const;

    /**
     * @brief Tests whether a position lies on the border.
     * @param Point is the position to test.
     * @param Tolerance is the maximum distance to the border in cm.
     * @return @c true if @c Point is within @c Tolerance of the border, otherwise @c false.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT bool IsOnBorder(const FVector2D& Point, double Tolerance) const;

    //~=============================================================================
    // Distance

    /**
     * @brief Finds the segment that is closest to a position.
     * @param Point is the position to measure from.
     * @return Index of the corner the closest segment starts at, @c INDEX_NONE if the polygon has no corners.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT int32 FindClosestSegment(const FVector2D& Point) const;

    /**
     * @brief Computes the squared distance from a position to the nearest point on the border.
     * @param Point is the position to measure from.
     * @return Distance in cm², @c 0 if @c Point lies on the border, also @c 0 if the polygon has no corners.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT double DistanceSquaredToBorder(const FVector2D& Point) const;

    /**
     * @brief Computes the squared distance from a position to the polygon area.
     * @param Point is the position to measure from.
     * @return Distance in cm², @c 0 if @c Point is inside or on the border.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT double DistanceSquaredToPoint(const FVector2D& Point) const;

private:
    /**
     * @brief Computes the index of the following corner, wrapping around at the end.
     * @param Index is the index of the current corner.
     * @return Index of the next corner.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT int32 NextIndex(int32 Index) const { return Index + 1 == Points.Num() ? 0 : Index + 1; }

    /**
     * @brief Computes the index of the preceding corner, wrapping around at the start.
     * @param Index is the index of the current corner.
     * @return Index of the previous corner.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT int32 PreviousIndex(int32 Index) const { return Index == 0 ? Points.Num() - 1 : Index - 1; }
    
    /** @brief Corner points in order in cm. */
    TArray<FVector2D> Points;
};