// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverPath.h"

#include "VectorUtil.h"
#include "Emberfall/Gameplay/World/Cover/CoverObject.h"


void UCoverPath::Initialize(const TArray<TWeakObjectPtr<ACoverObject>>& OrderedWalls)
{
    Segments.Reset();
    Length = 0.0f;

    if (OrderedWalls.IsEmpty())
    {
        return;
    }

    // Path direction from the first to the last wall; stays zero for a single wall
    FVector PathDirection = FVector::ZeroVector;

    const TWeakObjectPtr<ACoverObject>& FirstWall = OrderedWalls[0];
    const TWeakObjectPtr<ACoverObject>& LastWall = OrderedWalls.Last();

    FVector FirstWallMiddlePoint = FVector::ZeroVector;
    FVector LastWallMiddlePoint = FVector::ZeroVector;
    if (FirstWall != LastWall &&
        FirstWall.IsValid() && FirstWall->TryGetLocationOnLine(0.5f, FirstWallMiddlePoint) &&
        LastWall.IsValid() && LastWall->TryGetLocationOnLine(0.5f, LastWallMiddlePoint))
    {
        PathDirection = LastWallMiddlePoint - FirstWallMiddlePoint;
    }

    for (const TWeakObjectPtr<ACoverObject>& Wall : OrderedWalls)
    {
        if (!Wall.IsValid())
        {
            continue;
        }

        FVector From = FVector::ZeroVector;
        FVector To = FVector::ZeroVector;
        if (!Wall->TryGetLineEnds(From, To))
        {
            continue;
        }

        if (!PathDirection.IsNearlyZero() && FVector::DotProduct(To - From, PathDirection) < 0.0f)
        {
            Swap(From, To);
        }
        
        // Straight walls only: the length is the distance between the end points
        const float SegmentLength = FVector::Dist(From, To);
        if (SegmentLength <= UE_KINDA_SMALL_NUMBER)
        {
            continue;
        }
        
        FCoverPathSegment Segment{};
        Segment.Wall = Wall;
        Segment.StartDistance = Length;
        Segment.Length = SegmentLength;
        Segment.From = From;
        Segment.To = To;
        Segment.Normal = Wall->GetDockNormal();
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

        // Shadow of the player on the wall, clamped to the wall
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
