// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverSubsystem.h"
#include "Emberfall/Gameplay/World/Cover/CoverDebugDrawer.h"
#include "Emberfall/Gameplay/World/Cover/CoverGeometry.h"
#include "Emberfall/Gameplay/World/Cover/CoverGrouper.h"
#include "Emberfall/Gameplay/World/Cover/CoverLoop.h"
#include "Emberfall/Gameplay/World/Cover/CoverOutlineBuilder.h"
#include "Emberfall/Gameplay/World/Cover/CoverSettings.h"

#include "EngineUtils.h"


void UCoverSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    const UCoverSettings* Settings = GetDefault<UCoverSettings>();
    checkf(Settings, TEXT("UCoverSettings class default object is missing"));
    SpatialGrid = MakeUnique<FCoverSpatialGrid>(*Settings);
}

void UCoverSubsystem::Deinitialize()
{
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
    if (GetDefault<UCoverSettings>()->bDrawDebugGrid)
    {
        DrawDebug(-1.0f);
    }
#endif
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
        UE_LOG(LogTemp, Warning, TEXT("UCoverSubsystem: '%s' has no footprint, not registered"), *CoverObject->GetName());
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
        UE_LOG(LogTemp, Verbose, TEXT("UCoverSubsystem: unregistered '%s'"), *GetNameSafe(CoverObject));
    }

    return bRemoved;
}

void UCoverSubsystem::GetNearbyCoverObjects(const FVector& Position, float Radius,
    TArray<ACoverObject*>& OutCoverObjects) const
{
    if (SpatialGrid)
    {
        SpatialGrid->Query(Position, Radius, OutCoverObjects);
    }
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

    const UCoverSettings* Settings = GetDefault<UCoverSettings>();

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
    if (GetDefault<UCoverSettings>()->bDrawDebugGrid)
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

    const FCoverDebugDrawer Drawer(*GetWorld(), *GetDefault<UCoverSettings>());
    Drawer.DrawCells(*SpatialGrid, Duration);
    
    const TArray<FCoverGroup>& CurrentGroups = GetGroups();
    Drawer.DrawGroups(CurrentGroups, Duration);

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
        UE_LOG(LogTemp, Warning, TEXT("UCoverSubsystem: '%s' lost its footprint, unregistered"), *GetNameSafe(CoverObject));
        UnregisterCoverObject(CoverObject);
        return;
    }

    MarkGroupsDirty();
}
