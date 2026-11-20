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

void FPolyline2D::CollectSimplifiedIndices(double Tolerance, TArray<int32>& OutIndices) const
{
    OutIndices.Reset();

    // A closed path is simplified as an open one that returns to its start, the duplicate is dropped afterwards.
    TArray<FVector2D> Path;
    Path.Reserve(Points.Num() + 1);
    Path.Append(Points);
    if (bIsClosed && !Points.IsEmpty())
    {
        // Copied from Points, adding an element of the array itself would break when it reallocates.
        Path.Add(Points[0]);
    }

    const int32 PathNum = Path.Num();
    if (PathNum < 3)
    {
        for (int32 Index = 0; Index < GetPointNum(); ++Index)
        {
            OutIndices.Add(Index);
        }
        return;
    }

    TArray<bool> KeepPoints;
    KeepPoints.Init(false, PathNum);
    KeepPoints[0] = true;
    KeepPoints[PathNum - 1] = true;

    // Each entry is a range of indices that still has to be checked against its chord.
    TArray<TPair<int32, int32>> RangeStack;
    RangeStack.Emplace(0, PathNum - 1);

    while (!RangeStack.IsEmpty())
    {
        const TPair<int32, int32> Range = RangeStack.Pop();
        const FSegment2D Chord(Path[Range.Key], Path[Range.Value]);

        // A closed path has a degenerate first chord, its distance falls back to the start point,
        // so the point farthest from the start is the first one that gets kept.
        double FarthestDistance = 0.0;
        int32 FarthestIndex = INDEX_NONE;
        for (int32 Index = Range.Key + 1; Index < Range.Value; ++Index)
        {
            const double Distance = FMath::Abs(Chord.SignedDistanceToLine(Path[Index]));
            if (Distance > FarthestDistance)
            {
                FarthestDistance = Distance;
                FarthestIndex = Index;
            }
        }

        if (FarthestIndex != INDEX_NONE && FarthestDistance > Tolerance)
        {
            KeepPoints[FarthestIndex] = true;
            RangeStack.Emplace(Range.Key, FarthestIndex);
            RangeStack.Emplace(FarthestIndex, Range.Value);
        }
    }

    for (int32 Index = 0; Index < PathNum; ++Index)
    {
        if (KeepPoints[Index])
        {
            OutIndices.Add(Index);
        }
    }

    // The appended copy of the first point of a closed path is not a point of this polyline.
    if (bIsClosed)
    {
        OutIndices.Pop();
    }
}

FPolyline2D FPolyline2D::Simplify(double Tolerance) const
{
    TArray<int32> KeptIndices;
    CollectSimplifiedIndices(Tolerance, KeptIndices);

    TArray<FVector2D> KeptPoints;
    KeptPoints.Reserve(KeptIndices.Num());
    for (const int32 KeptIndex : KeptIndices)
    {
        KeptPoints.Add(Points[KeptIndex]);
    }

    return FPolyline2D(MoveTemp(KeptPoints), bIsClosed);
}
