// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Core/Geometry/Polygon2D.h"


const FPolygon2D FPolygon2D::Invalid = FPolygon2D(TArray<FVector2D>());

double FPolygon2D::GetSignedArea() const
{
    if (GetPointNum() < 3)
    {
        return 0.0;
    }
    
    double CrossSum = 0.0;
    for (int32 Index = 0; Index < GetPointNum(); ++Index)
    {
        const FSegment2D Segment = GetSegment(Index);
        const double Cross = FVector2D::CrossProduct(Segment.GetStart(), Segment.GetEnd());
        CrossSum += Cross;
    }
        
    const double SignedArea = CrossSum * 0.5;
    return SignedArea;
}

double FPolygon2D::GetPerimeter() const
{
    double Perimeter = 0.0;
    for (int32 Index = 0; Index < GetPointNum(); ++Index)
    {
        const FSegment2D Segment = GetSegment(Index);
        const double SegmentLength = Segment.GetLength();
        Perimeter += SegmentLength;
    }
    
    return Perimeter;
}

FVector2D FPolygon2D::GetCentroid() const
{
    if (GetPointNum() == 0)
    {
        return FVector2D::ZeroVector;
    }

    // Area-weighted average of the triangles (origin, start, end) of all segments.
    FVector2D WeightedSum = FVector2D::ZeroVector;
    double CrossSum = 0.0;
    for (int32 Index = 0; Index < GetPointNum(); ++Index)
    {
        const FSegment2D Segment = GetSegment(Index);
        const double Cross = FVector2D::CrossProduct(Segment.GetStart(), Segment.GetEnd());
        WeightedSum += (Segment.GetStart() + Segment.GetEnd()) * Cross;
        CrossSum += Cross;
    }

    const double SignedArea = CrossSum * 0.5;
    if (FMath::IsNearlyZero(SignedArea))
    {
        // Degenerate polygon (a line or a point), the formula would divide by zero.
        FVector2D PointSum = FVector2D::ZeroVector;
        for (const FVector2D& Point : Points)
        {
            PointSum += Point;
        }
        const FVector2D Average = PointSum / GetPointNum();
        return Average;
    }

    const FVector2D Centroid = WeightedSum / (6.0 * SignedArea);
    return Centroid;
}

FPolygon2D FPolygon2D::BuildOffset(double Distance) const
{
    const int32 PointNum = GetPointNum();
    if (PointNum < 3)
    {
        return FPolygon2D(Points);
    }

    // Computed once, GetSegmentOutwardNormal would recompute the area for every segment.
    const double OutwardSign = IsCounterClockwise() ? 1.0 : -1.0;

    // Every segment moved along its outward normal.
    TArray<FSegment2D> OffsetLines;
    OffsetLines.Reserve(PointNum);
    for (int32 Index = 0; Index < PointNum; ++Index)
    {
        const FSegment2D Segment = GetSegment(Index);
        const FVector2D Shift = Segment.GetRightNormal() * (OutwardSign * Distance);
        OffsetLines.Emplace(Segment.GetStart() + Shift, Segment.GetEnd() + Shift);
    }

    // New corner = intersection of the moved previous segment and the moved current segment.
    TArray<FVector2D> OffsetPoints;
    OffsetPoints.Reserve(PointNum);
    for (int32 Index = 0; Index < PointNum; ++Index)
    {
        const FSegment2D& PreviousLine = OffsetLines[PreviousIndex(Index)];
        const FSegment2D& CurrentLine = OffsetLines[Index];

        FVector2D Corner = FVector2D::ZeroVector;
        if (!PreviousLine.IntersectLines(CurrentLine, Corner))
        {
            // Parallel neighbors (collinear corner), the moved start of the current segment is already right.
            Corner = CurrentLine.GetStart();
        }
        OffsetPoints.Add(Corner);
    }

    return FPolygon2D(MoveTemp(OffsetPoints));
}

bool FPolygon2D::IsConvex() const
{
    if (GetPointNum() < 3)
    {
        return false;
    }

    bool bHasLeftTurn = false;
    bool bHasRightTurn = false;
    for (int32 Index = 0; Index < GetPointNum(); ++Index)
    {
        // The corner after the segment end shows in which direction the outline turns at the segment end.
        const FSegment2D Segment = GetSegment(Index);
        const FVector2D FollowingPoint = Points[NextIndex(NextIndex(Index))];
        const double Side = Segment.SideOfPoint(FollowingPoint);
        bHasLeftTurn |= Side > 0.0;
        bHasRightTurn |= Side < 0.0;
    }

    const bool bIsConvex = !(bHasLeftTurn && bHasRightTurn);
    return bIsConvex;
}

bool FPolygon2D::ContainsPoint(const FVector2D& Point) const
{
    bool bIsInside = false;
    for (int32 Index = 0; Index < GetPointNum(); ++Index)
    {
        const FSegment2D Segment = GetSegment(Index);
        const FVector2D Start = Segment.GetStart();
        const FVector2D End = Segment.GetEnd();

        // Only segments that cross the horizontal ray through Point can toggle the result.
        // This also guarantees End.Y != Start.Y, so the division below is safe.
        const bool bStartAbove = Start.Y > Point.Y;
        const bool bEndAbove = End.Y > Point.Y;
        if (bStartAbove == bEndAbove)
        {
            continue;
        }

        // X position where the segment crosses the ray's height, the ray runs to the right.
        const double Alpha = (Point.Y - Start.Y) / (End.Y - Start.Y);
        const double CrossingX = Start.X + Alpha * (End.X - Start.X);
        if (Point.X < CrossingX)
        {
            bIsInside = !bIsInside;
        }
    }

    return bIsInside;
}

bool FPolygon2D::IsOnBorder(const FVector2D& Point, double Tolerance) const
{
    const double DistanceSquared = DistanceSquaredToBorder(Point);
    const double ToleranceSquared = FMath::Square(Tolerance);
    const bool bIsOnBorder = DistanceSquared <= ToleranceSquared;
    return bIsOnBorder;
}

int32 FPolygon2D::FindClosestSegment(const FVector2D& Point) const
{
    int32 ClosestIndex = INDEX_NONE;
    double ClosestDistanceSquared = TNumericLimits<double>::Max();
    for (int32 Index = 0; Index < GetPointNum(); ++Index)
    {
        const FSegment2D Segment = GetSegment(Index);
        const double SegmentDistanceSquared = Segment.DistanceSquaredToPoint(Point);
        if (SegmentDistanceSquared < ClosestDistanceSquared)
        {
            ClosestIndex = Index;
            ClosestDistanceSquared = SegmentDistanceSquared;
        }
    }

    return ClosestIndex;
}

double FPolygon2D::DistanceSquaredToBorder(const FVector2D& Point) const
{
    const int32 ClosestIndex = FindClosestSegment(Point);
    if (ClosestIndex == INDEX_NONE)
    {
        return 0.0;
    }

    const double DistanceSquared = GetSegment(ClosestIndex).DistanceSquaredToPoint(Point);
    return DistanceSquared;
}

double FPolygon2D::DistanceSquaredToPoint(const FVector2D& Point) const
{
    if (ContainsPoint(Point))
    {
        return 0.0;
    }

    const double DistanceSquared = DistanceSquaredToBorder(Point);
    return DistanceSquared;
}