// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"


/**
 * @brief Straight line piece between two points in the ground plane.
 */
class FSegment2D
{
public:
    /**
     * @brief Creates a segment between two points.
     * @param InStart is the first end point in cm.
     * @param InEnd is the second end point in cm.
     */
    FSegment2D(const FVector2D& InStart, const FVector2D& InEnd)
        : Start(InStart), End(InEnd)
    {
    }

    //~=============================================================================
    // Validity
    
    /** @brief Segment with NaN end points that marks the absence of a segment. */
    static const FSegment2D Invalid;

    /**
     * @brief Tests whether both end points are finite numbers.
     * @return @c false if the segment is @c Invalid or has infinite end points, otherwise @c true.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT bool IsValid() const { return !Start.ContainsNaN() && !End.ContainsNaN(); }
    
    //~=============================================================================
    // Access

    /**
     * @brief Gets the first end point.
     * @return Start point in cm.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT const FVector2D& GetStart() const { return Start; }

    /**
     * @brief Gets the second end point.
     * @return End point in cm.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT const FVector2D& GetEnd() const { return End; }

    /**
     * @brief Gets the vector from the start to the end point.
     * @return Direction in cm, not normalized.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT FVector2D GetDirection() const { return End - Start; }

    //~=============================================================================
    // Shape

    /**
     * @brief Computes the length of the segment.
     * @return Length in cm.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT double GetLength() const
    {
        const double Length = GetDirection().Size();
        return Length;
    }

    /**
     * @brief Computes the point at a fraction along the segment.
     * @param Alpha is the fraction from @c Start (@c 0) to @c End (@c 1).
     * @return Point on the line through the segment in cm, outside of the segment if @c Alpha is not in [0, 1].
     */
    [[nodiscard]] UE_FORCEINLINE_HINT FVector2D GetPointAt(double Alpha) const
    {
        const FVector2D Point = Start + GetDirection() * Alpha;
        return Point;
    }

    /**
     * @brief Computes the midpoint of the segment.
     * @return Midpoint in cm.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT FVector2D GetMidpoint() const
    {
        const FVector2D Midpoint = GetPointAt(0.5);
        return Midpoint;
    }

    /**
     * @brief Computes the normalized normal pointing to the right of the segment direction.
     * @return Unit normal, @c ZeroVector if the segment is degenerate.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT FVector2D GetRightNormal() const
    {
        const FVector2D Direction = GetDirection();
        const FVector2D RightNormal = FVector2D(Direction.Y, -Direction.X).GetSafeNormal();
        return RightNormal;
    }

    /**
     * @brief Tests whether start and end coincide.
     * @return @c true if the length is practically @c 0, otherwise @c false.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT bool IsDegenerate() const
    {
        const bool bIsDegenerate = GetDirection().SizeSquared() < UE_KINDA_SMALL_NUMBER;
        return bIsDegenerate;
    }

    //~=============================================================================
    // Point queries

    /**
     * @brief Computes on which side of the segment a point lies, as the 2D cross product.
     * @param Point is the position to test.
     * @return Value in cm², positive if @c Point lies left of the segment seen from @c Start to @c End, negative if right, @c 0 if on the line through the segment.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT double SideOfPoint(const FVector2D& Point) const
    {
        const FVector2D SegmentDirection = GetDirection();
        const FVector2D PointDirection = Point - Start;
        return FVector2D::CrossProduct(SegmentDirection, PointDirection);
    }

    /**
     * @brief Computes the point on the segment that is closest to a position.
     * @param Point is the position to measure from.
     * @return Closest point on the segment in cm, @c Start or @c End if the closest point on the line lies beyond the ends.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT FVector2D GetClosestPoint(const FVector2D& Point) const
    {
        return FMath::ClosestPointOnSegment2D(Point, Start, End);
    }

    /**
     * @brief Computes the distance from a position to the segment.
     * @param Point is the position to measure from.
     * @return Distance in cm, @c 0 if @c Point lies on the segment.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT double DistanceToPoint(const FVector2D& Point) const
    {
        const double DistanceSquared = DistanceSquaredToPoint(Point);
        const double Distance = FMath::Sqrt(DistanceSquared);
        return Distance;
    }

    /**
     * @brief Computes the squared distance from a position to the segment.
     * @param Point is the position to measure from.
     * @return Distance in cm², @c 0 if @c Point lies on the segment.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT double DistanceSquaredToPoint(const FVector2D& Point) const
    {
        const FVector2D ClosestPoint = GetClosestPoint(Point);
        const double DistanceSquared = FVector2D::DistSquared(Point, ClosestPoint);
        return DistanceSquared;
    }

    /**
     * @brief Computes the signed distance from a position to the infinite line through the segment.
     * @param Point is the position to measure from.
     * @return Distance in cm, positive if @c Point lies left of the segment, negative if right, unsigned distance to @c Start if the segment is degenerate.
     */
    [[nodiscard]] UE_FORCEINLINE_HINT double SignedDistanceToLine(const FVector2D& Point) const
    {
        if (IsDegenerate())
        {
            return FVector2D::Distance(Point, Start);
        }

        const double SignedDistance = SideOfPoint(Point) / GetLength();
        return SignedDistance;
    }

    //~=============================================================================
    // Intersection

    /**
     * @brief Computes where the line through this segment meets the line through another segment.
     * @param Other is the segment whose line is intersected.
     * @param OutAlpha is filled with the crossing position along this segment, @c 0 at @c Start and @c 1 at @c End.
     * @param OutOtherAlpha is filled with the crossing position along @c Other, @c 0 at its start and @c 1 at its end.
     * @return @c true if the lines intersect in one point, @c false if they are parallel.
     */
    [[nodiscard]] bool IntersectLine(const FSegment2D& Other, double& OutAlpha, double& OutOtherAlpha) const;

    /**
     * @brief Tests whether this segment crosses another segment and computes where this segment is hit.
     * @param Other is the segment to test against.
     * @param OutAlpha is filled with the crossing position along this segment, @c 0 at @c Start and @c 1 at @c End.
     * @return @c true if the segments cross, @c false if they are parallel or do not reach each other.
     */
    [[nodiscard]] bool IntersectSegment(const FSegment2D& Other, double& OutAlpha) const;

    //~=============================================================================
    // Splitting

    /**
     * @brief Cuts the segment into consecutive pieces at the given positions along it.
     * @param Alphas is the list of split positions, @c 0 at @c Start and @c 1 at @c End, in any order, values outside of [0, 1] are clamped.
     * @return Pieces from @c Start to @c End, pieces without length are left out.
     */
    [[nodiscard]] TArray<FSegment2D> SplitAtAlphas(const TArray<double>& Alphas) const;

private:
    /** @brief First end point in cm. */
    FVector2D Start;
    /** @brief Second end point in cm. */
    FVector2D End;
};
