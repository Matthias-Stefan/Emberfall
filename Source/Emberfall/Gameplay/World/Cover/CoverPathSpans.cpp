// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverPathSpans.h"


FCoverPathSpans FCoverPathSpans::Build(const FPolyline2D& Path, bool bOutwardIsRightNormal,
    double MinCornerAngleDegrees, double CornerMargin)
{
    FCoverPathSpans Result;
    Result.bIsClosed = Path.IsClosed();
    Result.PathLength = Path.GetLength();
    if (!Path.IsValid() || Result.PathLength <= 0.0)
    {
        return Result;
    }

    TArray<double> PointDistances;
    Path.CollectPointDistances(PointDistances);

    // Distances of everything the unit has to stop in front of, in path order.
    TArray<double> Blockers;
    const int32 PointNum = Path.GetPointNum();
    for (int32 PointIndex = 0; PointIndex < PointNum; ++PointIndex)
    {
        const bool bIsPathEnd = !Path.IsClosed() && (PointIndex == 0 || PointIndex == PointNum - 1);
        if (bIsPathEnd)
        {
            Blockers.Add(PointDistances[PointIndex]);
            continue;
        }

        // The first point of a closed path is reached by its closing segment.
        const int32 IncomingIndex = PointIndex == 0 ? Path.GetSegmentNum() - 1 : PointIndex - 1;
        if (IsBlockingCorner(Path.GetSegment(IncomingIndex), Path.GetSegment(PointIndex), bOutwardIsRightNormal,
            MinCornerAngleDegrees))
        {
            Blockers.Add(PointDistances[PointIndex]);
        }
    }

    // A closed path without corners is walkable everywhere, an open path always has its two ends.
    if (Blockers.IsEmpty())
    {
        return Result;
    }

    const int32 BlockerNum = Blockers.Num();
    const int32 SpanNum = Path.IsClosed() ? BlockerNum : BlockerNum - 1;
    for (int32 SpanIndex = 0; SpanIndex < SpanNum; ++SpanIndex)
    {
        const double BlockerStart = Blockers[SpanIndex];
        double BlockerEnd = Blockers[(SpanIndex + 1) % BlockerNum];
        if (BlockerEnd <= BlockerStart)
        {
            // The closing span of a closed path runs over the end of the path to the first blocker.
            BlockerEnd += Result.PathLength;
        }

        FSpan Span;
        Span.Start = BlockerStart + CornerMargin;
        Span.End = BlockerEnd - CornerMargin;
        if (Span.End < Span.Start)
        {
            // Too short for both margins, the unit may only stand in the middle.
            Span.Start = 0.5 * (BlockerStart + BlockerEnd);
            Span.End = Span.Start;
        }

        Result.Spans.Add(Span);
    }

    return Result;
}

double FCoverPathSpans::FindNearestFreeDistance(double Distance) const
{
    if (Spans.IsEmpty())
    {
        return Distance;
    }

    // A closed path repeats every span one path length before and after.
    const int32 ShiftNum = bIsClosed ? 1 : 0;
    double BestGap = TNumericLimits<double>::Max();
    double BestDistance = Distance;
    for (const FSpan& Span : Spans)
    {
        for (int32 Shift = -ShiftNum; Shift <= ShiftNum; ++Shift)
        {
            const double ShiftedDistance = Distance + Shift * PathLength;
            const double Gap = Span.GetGap(ShiftedDistance);
            if (Gap < BestGap)
            {
                BestGap = Gap;
                BestDistance = FMath::Clamp(ShiftedDistance, Span.Start, Span.End);
            }
        }
    }

    return BestDistance;
}

double FCoverPathSpans::ComputeWalkDelta(double CurrentDistance, double TargetDistance) const
{
    if (Spans.IsEmpty())
    {
        double Delta = TargetDistance - CurrentDistance;
        if (bIsClosed && PathLength > 0.0)
        {
            // A closed path without corners has two ways to the target, take the shorter one.
            Delta = FMath::Fmod(Delta, PathLength);
            if (Delta > PathLength * 0.5)
            {
                Delta -= PathLength;
            }
            else if (Delta < -PathLength * 0.5)
            {
                Delta += PathLength;
            }
        }

        return Delta;
    }

    // A closed path repeats every span one path length before and after.
    const int32 ShiftNum = bIsClosed ? 1 : 0;

    // The span the unit stands in, with the unit's position in the frame of that span.
    const FSpan* CurrentSpan = nullptr;
    double CurrentInSpanFrame = 0.0;
    for (const FSpan& Span : Spans)
    {
        for (int32 Shift = -ShiftNum; Shift <= ShiftNum && !CurrentSpan; ++Shift)
        {
            const double ShiftedDistance = CurrentDistance + Shift * PathLength;
            if (Span.GetGap(ShiftedDistance) <= UE_KINDA_SMALL_NUMBER)
            {
                CurrentSpan = &Span;
                CurrentInSpanFrame = ShiftedDistance;
            }
        }

        if (CurrentSpan)
        {
            break;
        }
    }

    if (!CurrentSpan)
    {
        return 0.0;
    }

    // On a closed path the target has several equivalent distances, take the one closest to the span and clamp it.
    double BestGap = TNumericLimits<double>::Max();
    double BestTarget = TargetDistance;
    for (int32 Shift = -ShiftNum; Shift <= ShiftNum; ++Shift)
    {
        const double ShiftedTarget = TargetDistance + Shift * PathLength;
        const double Gap = CurrentSpan->GetGap(ShiftedTarget);
        if (Gap < BestGap)
        {
            BestGap = Gap;
            BestTarget = ShiftedTarget;
        }
    }

    const double ClampedTarget = FMath::Clamp(BestTarget, CurrentSpan->Start, CurrentSpan->End);
    return ClampedTarget - CurrentInSpanFrame;
}

bool FCoverPathSpans::IsBlockingCorner(const FSegment2D& IncomingSegment, const FSegment2D& OutgoingSegment,
    bool bOutwardIsRightNormal, double MinCornerAngleDegrees)
{
    const FVector2D IncomingDirection = IncomingSegment.GetDirection().GetSafeNormal();
    const FVector2D OutgoingDirection = OutgoingSegment.GetDirection().GetSafeNormal();
    const double Cosine = FMath::Clamp(FVector2D::DotProduct(IncomingDirection, OutgoingDirection), -1.0, 1.0);
    const double TurnAngle = FMath::RadiansToDegrees(FMath::Acos(Cosine));
    if (TurnAngle < MinCornerAngleDegrees)
    {
        return false;
    }

    // Only a turn toward the wall exposes the unit, in an inner corner the next wall is already there.
    const FVector2D RightNormal = IncomingSegment.GetRightNormal();
    const FVector2D OutwardNormal = bOutwardIsRightNormal ? RightNormal : -RightNormal;
    return FVector2D::DotProduct(OutgoingDirection, OutwardNormal) < 0.0;
}
