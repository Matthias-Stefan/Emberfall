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

FPolygon2D FPolygon2D::BuildOffset(double Distance, double MiterLimit) const
{
    const int32 PointNum = GetPointNum();
    if (PointNum < 3)
    {
        return FPolygon2D::Invalid;
    }

    // Computed once, GetSegmentOutwardNormal would recompute the area for every segment.
    const bool bCounterClockwise = IsCounterClockwise();
    const double OutwardSign = bCounterClockwise ? 1.0 : -1.0;

    TArray<FSegment2D> OffsetLines;
    OffsetLines.Reserve(PointNum);
    for (int32 Index = 0; Index < PointNum; ++Index)
    {
        const FSegment2D Segment = GetSegment(Index);
        const FVector2D Shift = Segment.GetRightNormal() * (OutwardSign * Distance);
        OffsetLines.Emplace(Segment.GetStart() + Shift, Segment.GetEnd() + Shift);
    }

    const double MaxShiftSquared = FMath::Square(FMath::Abs(Distance) * MiterLimit);

    TArray<FVector2D> OffsetPoints;
    OffsetPoints.Reserve(PointNum);
    for (int32 Index = 0; Index < PointNum; ++Index)
    {
        const FSegment2D& PreviousLine = OffsetLines[PreviousIndex(Index)];
        const FSegment2D& CurrentLine = OffsetLines[Index];

        double Alpha = 0.0;
        double OtherAlpha = 0.0;
        FVector2D Corner = CurrentLine.GetStart();
        if (PreviousLine.IntersectLine(CurrentLine, Alpha, OtherAlpha))
        {
            Corner = PreviousLine.GetPointAt(Alpha);
        }
        // else: parallel neighbors (collinear corner), the moved start of the current segment is already right.

        // Very sharp corners shoot far away from the original corner.
        if (FVector2D::DistSquared(Corner, Points[Index]) > MaxShiftSquared)
        {
            return FPolygon2D::Invalid;
        }
        OffsetPoints.Add(Corner);
    }

    // Shrinking too far flips the winding, the result would be inside out.
    FPolygon2D Result(MoveTemp(OffsetPoints));
    if (Result.IsCounterClockwise() != bCounterClockwise)
    {
        return FPolygon2D::Invalid;
    }
    return Result;
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

FVector2D FPolygon2D::GetClosestPoint(const FVector2D& Point) const
{
    if (ContainsPoint(Point))
    {
        return Point;
    }

    const int32 ClosestIndex = FindClosestSegment(Point);
    if (ClosestIndex == INDEX_NONE)
    {
        return FVector2D::ZeroVector;
    }

    const FVector2D ClosestPoint = GetSegment(ClosestIndex).GetClosestPoint(Point);
    return ClosestPoint;
}

double FPolygon2D::DistanceSquaredToPolygon(const FPolygon2D& Other) const
{
    // Nothing to measure to, an empty polygon is infinitely far away instead of touching everything.
    if (GetPointNum() == 0 || Other.GetPointNum() == 0)
    {
        return TNumericLimits<double>::Max();
    }

    // One polygon completely inside the other, a single corner is enough to tell.
    if (ContainsPoint(Other.GetPoint(0)) || Other.ContainsPoint(GetPoint(0)))
    {
        return 0.0;
    }

    double ClosestDistanceSquared = TNumericLimits<double>::Max();
    for (int32 Index = 0; Index < GetPointNum(); ++Index)
    {
        const FSegment2D Segment = GetSegment(Index);
        for (int32 OtherIndex = 0; OtherIndex < Other.GetPointNum(); ++OtherIndex)
        {
            const FSegment2D OtherSegment = Other.GetSegment(OtherIndex);

            // Crossing borders mean the polygons overlap.
            double Alpha = 0.0;
            if (Segment.IntersectSegment(OtherSegment, Alpha))
            {
                return 0.0;
            }

            // Without a crossing, the closest pair of two segments always involves an end point.
            ClosestDistanceSquared = FMath::Min(ClosestDistanceSquared,
                                                OtherSegment.DistanceSquaredToPoint(Segment.GetStart()));
            ClosestDistanceSquared = FMath::Min(ClosestDistanceSquared,
                                                OtherSegment.DistanceSquaredToPoint(Segment.GetEnd()));
            ClosestDistanceSquared = FMath::Min(ClosestDistanceSquared,
                                                Segment.DistanceSquaredToPoint(OtherSegment.GetStart()));
            ClosestDistanceSquared = FMath::Min(ClosestDistanceSquared,
                                                Segment.DistanceSquaredToPoint(OtherSegment.GetEnd()));
        }
    }

    return ClosestDistanceSquared;
}

bool FPolygon2D::IntersectSegment(const FSegment2D& Segment, TArray<double>& OutAlphas) const
{
    OutAlphas.Reset();
    for (int32 Index = 0; Index < GetPointNum(); ++Index)
    {
        // The alpha must be measured along the queried segment, so it is the one that calls.
        double Alpha = 0.0;
        if (Segment.IntersectSegment(GetSegment(Index), Alpha))
        {
            OutAlphas.Add(Alpha);
        }
    }

    OutAlphas.Sort();

    // A crossing exactly through a corner is found by both neighboring segments.
    for (int32 Index = OutAlphas.Num() - 1; Index > 0; --Index)
    {
        if (FMath::IsNearlyEqual(OutAlphas[Index], OutAlphas[Index - 1], UE_KINDA_SMALL_NUMBER))
        {
            OutAlphas.RemoveAt(Index);
        }
    }

    return !OutAlphas.IsEmpty();
}
