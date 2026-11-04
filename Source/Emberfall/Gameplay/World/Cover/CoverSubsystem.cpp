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
}

#if ENABLE_DRAW_DEBUG
void UCoverSubsystem::DrawDebug(float Duration) const
{
    if (!SpatialGrid)
    {
        return;
    }

    const FCoverDebugDrawer Drawer(*GetWorld(), *GetDefault<UCoverSettings>());
    Drawer.DrawCells(*SpatialGrid, Duration);
    Drawer.DrawGroups(Groups, Duration);

    for (const FCoverGroup& Group : Groups)
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