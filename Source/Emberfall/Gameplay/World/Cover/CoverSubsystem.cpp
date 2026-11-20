// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverSubsystem.h"

#include "Emberfall/Gameplay/World/Cover/CoverGeometry.h"
#include "Emberfall/Gameplay/World/Cover/CoverDebugDrawer.h"
#include "Emberfall/Gameplay/World/Cover/CoverGrouper.h"
#include "Emberfall/Gameplay/World/Cover/CoverLog.h"
#include "Emberfall/Gameplay/World/Cover/CoverOutlineBuilder.h"
#include "Emberfall/Gameplay/World/Cover/CoverSettings.h"
#include "Emberfall/Gameplay/World/Cover/CoverTypes.h"

#include "EngineUtils.h"


void UCoverSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    Settings = GetDefault<UCoverSettings>();
    checkf(Settings, TEXT("UCoverSettings class default object is missing"));
    SpatialGrid = MakeUnique<FCoverSpatialGrid>(*Settings);
}

void UCoverSubsystem::Deinitialize()
{
    for (const TObjectPtr<ACoverObject>& CoverObject : CoverObjects)
    {
        if (CoverObject)
        {
            CoverObject->RemoveChangedListeners(this);
        }
    }
    
    Groups.Empty();
    SpatialGrid.Reset();
    CoverObjects.Empty();
    bGroupsDirty = false;

    Super::Deinitialize();
}

void UCoverSubsystem::OnWorldBeginPlay(UWorld& InWorld)
{
    Super::OnWorldBeginPlay(InWorld);

    TArray<ACoverObject*> FoundCoverObjects;
    CollectCoverObjects(FoundCoverObjects);
    for (ACoverObject* CoverObject : FoundCoverObjects)
    {
        RegisterCoverObject(CoverObject);
    }

    RebuildGroups();

#if ENABLE_DRAW_DEBUG
    if (Settings->bDrawDebugGrid)
    {
        DrawDebug(-1.0f);
    }
#endif
}

const UCoverSettings& UCoverSubsystem::GetSettings() const
{
    check(Settings);
    return *Settings;
}

bool UCoverSubsystem::RegisterCoverObject(ACoverObject* CoverObject)
{
    if (!IsValid(CoverObject) || !SpatialGrid)
    {
        return false;
    }

    bool bAlreadyRegistered = false;
    CoverObjects.Add(CoverObject, &bAlreadyRegistered);
    if (bAlreadyRegistered)
    {
        return false;
    }

    if (!SpatialGrid->Insert(CoverObject))
    {
        CoverObjects.Remove(CoverObject);
        UE_LOG(LogCover, Warning, TEXT("UCoverSubsystem: '%s' has no footprint, not registered"), *CoverObject->GetName());
        return false;
    }
    CoverObject->AddChangedListener(this, &UCoverSubsystem::HandleCoverObjectChanged);
    
    MarkGroupsDirty();
    return true;
}

bool UCoverSubsystem::UnregisterCoverObject(ACoverObject* CoverObject)
{
    if (!CoverObject)
    {
        return false;
    }

    if (SpatialGrid)
    {
        SpatialGrid->Remove(CoverObject);
    }

    const bool bRemoved = CoverObjects.Remove(CoverObject) > 0;
    if (bRemoved)
    {
        CoverObject->RemoveChangedListeners(this);
        MarkGroupsDirty();
        UE_LOG(LogCover, Verbose, TEXT("UCoverSubsystem: unregistered '%s'"), *GetNameSafe(CoverObject));
    }

    return bRemoved;
}

void UCoverSubsystem::QueryCoverObjectsInGrid(const FVector& Position, float Radius,
    TArray<ACoverObject*>& OutCoverObjects) const
{
    if (SpatialGrid)
    {
        SpatialGrid->Query(Position, Radius, OutCoverObjects);
    }
}

void UCoverSubsystem::QueryCoverObjectsInDistance(const FVector& Position, float MaxDistance,
    TArray<ACoverObject*>& OutCoverObjects) const
{
    // The query square with half edge MaxDistance fully contains the query circle,
    // so the grid never misses a matching object.
    TArray<ACoverObject*> Candidates;
    QueryCoverObjectsInGrid(Position, MaxDistance, Candidates);

    const float MaxDistanceSquared = FMath::Square(MaxDistance);

    // Reused for every candidate, so the array allocates only once.
    TArray<FVector> FootprintCorners;
    for (ACoverObject* Candidate : Candidates)
    {
        // An object without a mesh has no footprint and cannot be a cover.
        if (!Candidate->GetFootprintCorners(FootprintCorners))
        {
            continue;
        }

        const FPolygon2D Footprint = FCoverGeometry::ToPolygon2D(FootprintCorners);
        if (!Footprint.IsValid())
        {
            continue;
        }

        const double DistanceSquared = Footprint.DistanceSquaredToPoint(FVector2D(Position.X, Position.Y));
        if (DistanceSquared <= MaxDistanceSquared)
        {
            OutCoverObjects.Add(Candidate);
        }
    }
}

void UCoverSubsystem::QueryCoverEdgesInDistance(const FVector& Position, float MaxDistance,
    TArray<FCoverEdgeHit>& OutHits) const
{
    TArray<ACoverObject*> Candidates;
    QueryCoverObjectsInGrid(Position, MaxDistance, Candidates);

    const FVector2D Point(Position.X, Position.Y);
    TArray<FVector> Corners;
    TArray<bool> EdgeEnabled;

    for (ACoverObject* Candidate : Candidates)
    {
        if (!Candidate->GetFootprintEdges(Corners, EdgeEnabled))
        {
            continue;
        }

        FVector Center = FVector::ZeroVector;
        for (const FVector& Corner : Corners)
        {
            Center += Corner;
        }
        Center /= Corners.Num();

        for (int32 EdgeIndex = 0; EdgeIndex < Corners.Num(); ++EdgeIndex)
        {
            if (!EdgeEnabled[EdgeIndex])
            {
                continue;
            }

            const FVector& Start = Corners[EdgeIndex];
            const FVector& End = Corners[(EdgeIndex + 1) % Corners.Num()];
            const FSegment2D Edge(FVector2D(Start.X, Start.Y), FVector2D(End.X, End.Y));
            const FVector2D ClosestPoint = Edge.GetClosestPoint(Point);

            const double Distance = FVector2D::Distance(Point, ClosestPoint);
            if (Distance > MaxDistance)
            {
                continue;
            }

            // Same outward normal as in GetFootprintEdges: from the center to the edge middle.
            const FVector EdgeMiddle = (Start + End) * 0.5;

            FCoverEdgeHit EdgeHit;
            EdgeHit.CoverObject = Candidate;
            EdgeHit.EdgeIndex = EdgeIndex;
            EdgeHit.ClosestPoint = ClosestPoint;
            EdgeHit.OutwardNormal = FVector2D(EdgeMiddle.X - Center.X, EdgeMiddle.Y - Center.Y).GetSafeNormal();
            EdgeHit.Distance = Distance;
            OutHits.Add(EdgeHit);
        }
    }
}

bool UCoverSubsystem::FindNearestCoverEdge(const FVector& Position, float MaxDistance,
    FCoverEdgeHit& OutHit) const
{
    TArray<FCoverEdgeHit> EdgeHits;
    QueryCoverEdgesInDistance(Position, MaxDistance, EdgeHits);

    const FCoverEdgeHit* NearestHit = Algo::MinElementBy(EdgeHits, &FCoverEdgeHit::Distance);
    if (!NearestHit)
    {
        return false;
    }

    OutHit = *NearestHit;
    return true;
}

void UCoverSubsystem::RebuildGroups()
{
    // Cleared first, so reading the groups while rebuilding (debug drawing) does not trigger another rebuild.
    bGroupsDirty = false;
    
    Groups.Reset();
    if (!SpatialGrid)
    {
        return;
    }

    TArray<ACoverObject*> Objects;
    Objects.Reserve(CoverObjects.Num());
    for (const TObjectPtr<ACoverObject>& CoverObject : CoverObjects)
    {
        if (IsValid(CoverObject))
        {
            Objects.Add(CoverObject);
        }
    }

    const FCoverGrouper Grouper(*SpatialGrid, *Settings);
    Grouper.Build(Objects, Groups);

    const FCoverOutlineBuilder OutlineBuilder(*Settings);
    for (FCoverGroup& Group : Groups)
    {
        TArray<FCoverLoop> Loops;
        OutlineBuilder.Build(Group, Loops);
        Group.SetLoops(MoveTemp(Loops));
    }
    
#if ENABLE_DRAW_DEBUG
    if (Settings->bDrawDebugGrid)
    {
        FlushPersistentDebugLines(GetWorld());
        FlushDebugStrings(GetWorld());
        DrawDebug(-1.0f);
    }
#endif
}

const TArray<FCoverGroup>& UCoverSubsystem::GetGroups()
{
    if (bGroupsDirty)
    {
        RebuildGroups();
    }

    return Groups;
}

void UCoverSubsystem::MarkGroupsDirty()
{
    if (bGroupsDirty)
    {
        return;
    }

    const UWorld* World = GetWorld();
    if (!World)
    {
        return;
    }

    bGroupsDirty = true;

    TWeakObjectPtr<UCoverSubsystem> WeakThis(this);
    World->GetTimerManager().SetTimerForNextTick([WeakThis]()
    {
        if (UCoverSubsystem* Subsystem = WeakThis.Get())
        {
            Subsystem->GetGroups();
        }
    });
}

#if ENABLE_DRAW_DEBUG
void UCoverSubsystem::DrawDebug(float Duration)
{
    if (!SpatialGrid)
    {
        return;
    }

    const FCoverDebugDrawer Drawer(*GetWorld(), *Settings);
    Drawer.DrawCells(*SpatialGrid, Duration);
    
    const TArray<FCoverGroup>& CurrentGroups = GetGroups();
    Drawer.DrawGroups(CurrentGroups, Duration);
    Drawer.DrawEnabledSides(CurrentGroups, Duration);

    for (const FCoverGroup& Group : CurrentGroups)
    {
        Drawer.DrawLoops(Group.GetLoops(), Duration);
    }
}
#endif

void UCoverSubsystem::CollectCoverObjects(TArray<ACoverObject*>& OutCoverObjects) const
{
    for (TActorIterator<ACoverObject> It(GetWorld()); It; ++It)
    {
        OutCoverObjects.Add(*It);
    }
}

void UCoverSubsystem::HandleCoverObjectChanged(ACoverObject* CoverObject)
{
    if (!SpatialGrid || !CoverObject || !CoverObjects.Contains(CoverObject))
    {
        return;
    }

    // The grid keeps the cells of the position at registration, so the object has to leave and re-enter.
    SpatialGrid->Remove(CoverObject);
    if (!SpatialGrid->Insert(CoverObject))
    {
        // Without a footprint the object cannot stay in the grid, keep registry and grid consistent.
        UE_LOG(LogCover, Warning, TEXT("UCoverSubsystem: '%s' lost its footprint, unregistered"), *GetNameSafe(CoverObject));
        UnregisterCoverObject(CoverObject);
        return;
    }

    MarkGroupsDirty();
}
