// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverPath.h"
#include "Emberfall/Gameplay/World/Cover/CoverObjectTypes.h"


void UCoverPath::Initialize(const FCoverRun& Run)
{
    Segments.Reset();
    Length = 0.0f;
    bClosed = Run.bClosed;

    const int32 EdgeCount = Run.EdgeNormals.Num();
    if (EdgeCount == 0 || Run.Points.Num() < 2)
    {
        return;
    }

    for (int32 Edge = 0; Edge < EdgeCount; ++Edge)
    {
        // Closed runs wrap: the last edge ends at the first point
        const FVector From = Run.Points[Edge];
        const FVector To = Run.Points[(Edge + 1) % Run.Points.Num()];

        const float SegmentLength = FVector::Dist(From, To);
        if (SegmentLength <= UE_KINDA_SMALL_NUMBER)
        {
            continue;
        }

        FCoverPathSegment Segment{};
        Segment.StartDistance = Length;
        Segment.Length = SegmentLength;
        Segment.From = From;
        Segment.To = To;
        Segment.Normal = Run.EdgeNormals[Edge];
        Segments.Add(Segment);

        Length += SegmentLength;
    }
}

float UCoverPath::FindDistanceClosestTo(const FVector& WorldLocation) const
{
    float BestDistToPathSq = TNumericLimits<float>::Max();
    float BestDistanceAlongPath = 0.0f;

    for (const FCoverPathSegment& Segment : Segments)
    {
        const FVector SegmentDirection = (Segment.To - Segment.From).GetSafeNormal();
        const FVector ToPlayer = WorldLocation - Segment.From;

        // Shadow of the player on the edge, clamped to the edge
        float DistanceOnSegment = FVector::DotProduct(ToPlayer, SegmentDirection);
        DistanceOnSegment = FMath::Clamp(DistanceOnSegment, 0.0f, Segment.Length);

        const FVector ClosestPoint = Segment.From + SegmentDirection * DistanceOnSegment;
        const float DistToSegmentSq = FVector::DistSquared(WorldLocation, ClosestPoint);
        if (DistToSegmentSq < BestDistToPathSq)
        {
            BestDistToPathSq = DistToSegmentSq;
            BestDistanceAlongPath = Segment.StartDistance + DistanceOnSegment;
        }
    }

    return BestDistanceAlongPath;
}

FVector UCoverPath::GetLocationAtDistance(float Distance) const
{
    Distance = WrapDistance(Distance);

    const FCoverPathSegment* Segment = GetSegmentAtDistance(Distance);
    if (Segment == nullptr)
    {
        return FVector::ZeroVector;
    }

    const float T = FMath::Clamp((Distance - Segment->StartDistance) / Segment->Length, 0.0f, 1.0f);
    return FMath::Lerp(Segment->From, Segment->To, T);
}

FVector UCoverPath::GetNormalAtDistance(float Distance) const
{
    Distance = WrapDistance(Distance);

    const FCoverPathSegment* Segment = GetSegmentAtDistance(Distance);
    if (Segment == nullptr)
    {
        return FVector::ZeroVector;
    }

    return Segment->Normal;
}

const FCoverPathSegment* UCoverPath::GetSegmentAtDistance(float Distance) const
{
    if (Segments.IsEmpty())
    {
        return nullptr;
    }

    // Last segment that begins at or before Distance; segments are ordered by StartDistance
    const FCoverPathSegment* Found = &Segments[0];
    for (const FCoverPathSegment& Segment : Segments)
    {
        if (Segment.StartDistance > Distance)
        {
            break;
        }
        Found = &Segment;
    }

    return Found;
}

float UCoverPath::WrapDistance(float Distance) const
{
    if (!bClosed || Length <= UE_KINDA_SMALL_NUMBER)
    {
        return Distance;
    }

    const float Wrapped = FMath::Fmod(Distance, Length);
    return Wrapped < 0.0f ? Wrapped + Length : Wrapped;
}