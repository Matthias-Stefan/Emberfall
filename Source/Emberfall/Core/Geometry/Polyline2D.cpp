// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Core/Geometry/Polyline2D.h"
#include "Emberfall/Core/Geometry/Segment2D.h"


const FPolyline2D FPolyline2D::Invalid = FPolyline2D(TArray<FVector2D>(), false);

double FPolyline2D::GetLength() const
{
    double Length = 0.0;
    for (int32 Index = 0; Index < GetSegmentNum(); ++Index)
    {
        const FSegment2D Segment = GetSegment(Index);
        Length += Segment.GetLength();
    }
    
    return Length;
}

FVector2D FPolyline2D::GetPointAtDistance(double Distance) const
{
    if (GetSegmentNum() == 0)
    {
        return Points.IsEmpty() ? FVector2D::ZeroVector : Points[0];
    }
    
    const double TotalLength = GetLength();
    if (FMath::IsNearlyZero(TotalLength))
    {
        return Points[0];
    }
    
    // Open paths stop at the ends, closed paths wrap around.
    double Remaining = Distance;
    if (bIsClosed)
    {
        Remaining = FMath::Fmod(Distance, TotalLength);
        if (Remaining < 0.0)
        {
            Remaining += TotalLength;
        }
    }
    else
    {
        Remaining = FMath::Clamp(Distance, 0.0, TotalLength);
    }
    
    // Walk the segments, subtracting each length until the rest fits into one.
    for (int32 Index = 0; Index < GetSegmentNum(); ++Index)
    {
        const FSegment2D Segment = GetSegment(Index);
        const double SegmentLength = Segment.GetLength();
        if (SegmentLength > 0.0 && Remaining <= SegmentLength)
        {
            const double Alpha = Remaining / SegmentLength;
            const FVector2D Point = Segment.GetPointAt(Alpha);
            return Point;
        }

        Remaining -= SegmentLength;
    }
    
    // Rounding drift can leave a tiny rest after the last segment.
    const FVector2D EndPoint = GetSegment(GetSegmentNum() - 1).GetEnd();
    return EndPoint;
}

FVector2D FPolyline2D::FindClosestPoint(const FVector2D& Point, double& OutDistanceAlong) const
{
    OutDistanceAlong = 0.0;
    if (GetSegmentNum() == 0)
    {
        return Points.IsEmpty() ? FVector2D::ZeroVector : Points[0];
    }
    
    FVector2D ClosestPoint = Points[0];
    double ClosestDistanceSquared = TNumericLimits<double>::Max();
    double LengthBefore = 0.0;   // summed length of all segments before the current one
    for (int32 Index = 0; Index < GetSegmentNum(); ++Index)
    {
        const FSegment2D Segment = GetSegment(Index);
        const FVector2D CandidatePoint = Segment.GetClosestPoint(Point);
        const double CandidateDistanceSquared = FVector2D::DistSquared(Point, CandidatePoint);
        if (CandidateDistanceSquared < ClosestDistanceSquared)
        {
            ClosestPoint = CandidatePoint;
            ClosestDistanceSquared = CandidateDistanceSquared;
            OutDistanceAlong = LengthBefore + FVector2D::Distance(Segment.GetStart(), CandidatePoint);
        }

        LengthBefore += Segment.GetLength();
    }

    return ClosestPoint;
}
