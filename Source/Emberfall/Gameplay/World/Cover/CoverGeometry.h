// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"


/**
 * @brief Straight piece of an edge between two points.
 */
struct FCoverEdgePiece
{
    /** @brief Start point of the piece. */
    FVector Start = FVector::ZeroVector;

    /** @brief End point of the piece. */
    FVector End = FVector::ZeroVector;
};

/**
 * @brief Pure 2D helpers for cover footprints; ignores Z and holds no state.
 */
class EMBERFALL_API FCoverGeometry
{
public:
    /**
     * @brief Deleted, this class only provides static functions.
     */
    FCoverGeometry() = delete;

    // CoverGeometry.h, public
    /**
     * @brief Tests whether a point lies inside or on the border of a convex quad.
     * @param QuadCorners is the list of the four quad corners, either winding order.
     * @param Point is the position to test.
     * @return @c true if @c Point is inside or on the border, @c false if outside or fewer than three corners are given.
     */
    static bool ContainsPoint2D(const TArray<FVector>& QuadCorners, const FVector& Point);
    
    /**
     * @brief Tests whether a point lies strictly inside a convex quad, points on the border do not count.
     * @param QuadCorners is the list of the four quad corners, either winding order.
     * @param Point is the position to test.
     * @param BorderTolerance is the distance to every edge in cm below which the point counts as on the border.
     * @return @c true if @c Point is farther than @c BorderTolerance inside every edge, otherwise @c false.
     */
    static bool ContainsPointStrict2D(const TArray<FVector>& QuadCorners, const FVector& Point, double BorderTolerance);
    
    /**
     * @brief Computes the squared distance between two convex quads.
     * @param FirstQuadCorners is the list of the four corners of the first quad.
     * @param SecondQuadCorners is the list of the four corners of the second quad.
     * @return Squared distance in cm², @c 0 if the quads touch or overlap.
     */
    static double DistanceSquared2D(const TArray<FVector>& FirstQuadCorners, const TArray<FVector>& SecondQuadCorners);
    
    /**
     * @brief Tests whether two edges cross and computes where the first edge is hit.
     * @param FirstStart is the start point of the first edge.
     * @param FirstEnd is the end point of the first edge.
     * @param SecondStart is the start point of the second edge.
     * @param SecondEnd is the end point of the second edge.
     * @param OutFirstFraction is filled with the crossing position along the first edge, @c 0 at @c FirstStart and @c 1 at @c FirstEnd.
     * @return @c true if the edges cross, @c false if they are parallel or do not reach each other.
     */
    static bool EdgeIntersect2D(const FVector& FirstStart, const FVector& FirstEnd,
        const FVector& SecondStart, const FVector& SecondEnd, double& OutFirstFraction);
    
    /**
     * @brief Splits an edge into consecutive pieces at the given positions along it.
     * @param EdgeStart is the start point of the edge.
     * @param EdgeEnd is the end point of the edge.
     * @param Fractions is the list of split positions along the edge, @c 0 at @c EdgeStart and @c 1 at @c EdgeEnd, in any order.
     * @param OutPieces is filled with the pieces from @c EdgeStart to @c EdgeEnd, previous content is discarded.
     */
    static void SplitEdgeAtFractions2D(const FVector& EdgeStart, const FVector& EdgeEnd,
        const TArray<double>& Fractions, TArray<FCoverEdgePiece>& OutPieces);
    
    /**
     * @brief Tests whether a point lies on the border of a closed loop.
     * @param LoopCorners is the list of the loop corners, in order.
     * @param Point is the position to test.
     * @param BorderTolerance is the distance to an edge in cm below which the point counts as on the border.
     * @return @c true if @c Point is at most @c BorderTolerance away from any edge, otherwise @c false.
     */
    static bool IsOnBorder2D(const TArray<FVector>& LoopCorners, const FVector& Point, double BorderTolerance);
    
    /**
     * @brief Pushes every edge of a convex polygon outward and intersects neighboring edges, keeping the corners sharp.
     * @param ConvexCorners is the list of the polygon corners, either winding order.
     * @param Offset is the distance each edge is pushed outward in cm.
     * @param OutLoop is filled with the corners of the grown polygon, in the winding order of positive signed area.
     * @return @c true if the polygon was grown, @c false if fewer than three corners or a corner is a spike.
     */
    static bool BuildOffsetPolygon2D(const TArray<FVector>& ConvexCorners, double Offset, TArray<FVector>& OutLoop);
    
    /**
     * @brief Computes the distance of a point to the infinite line through two points.
     * @param Point is the position to measure from.
     * @param LineStart is the first point on the line.
     * @param LineEnd is the second point on the line.
     * @return Distance in cm, the distance to @c LineStart if both line points coincide.
     */
    static double DistanceToLine2D(const FVector& Point, const FVector& LineStart, const FVector& LineEnd);

    /**
     * @brief Removes points from an open polyline that deviate less than a tolerance from the simplified line.
     * @param Points is the list of polyline points in order.
     * @param Tolerance is the largest distance in cm a dropped point may have from the simplified line.
     * @param OutPoints is filled with the kept points in order, first and last point are always kept.
     */
    static void SimplifyPolyline2D(const TArray<FVector>& Points, double Tolerance, TArray<FVector>& OutPoints);
    
    /**
     * @brief Computes the area enclosed by a closed polygon, ignoring Z.
     * @param Points is the list of polygon corners in order, the last one connects back to the first.
     * @return Area in cm², always positive regardless of the winding.
     */
    static double Area2D(const TArray<FVector>& Points);
};
