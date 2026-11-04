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

    SpatialGrid->Insert(CoverObject);
    return true;
}

bool UCoverSubsystem::UnregisterCoverObject(ACoverObject* CoverObject)
{
    if (SpatialGrid)
    {
        SpatialGrid->Remove(CoverObject);
    }
    return CoverObjects.Remove(CoverObject) > 0;
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

    const FCoverGrouper Grouper(*SpatialGrid, *GetDefault<UCoverSettings>());
    Grouper.Build(Objects, Groups);
}

#if ENABLE_DRAW_DEBUG
void UCoverSubsystem::DrawDebug(float Duration) const
{
    if (!SpatialGrid)
    {
        return;
    }

    const UCoverSettings* Settings = GetDefault<UCoverSettings>();
    const FCoverDebugDrawer Drawer(*GetWorld(), *Settings);
    Drawer.DrawCells(*SpatialGrid, Duration);
    Drawer.DrawGroups(Groups, Duration);

    const FCoverOutlineBuilder Builder(*Settings);
    for (const FCoverGroup& Group : Groups)
    {
        TArray<FCoverLoop> OutlineLoops;
        Builder.Build(Group, OutlineLoops);
        Drawer.DrawLoops(OutlineLoops, Duration);
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