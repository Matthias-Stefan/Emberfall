// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverSubsystem.h"

#include "Emberfall/Gameplay/World/Cover/CoverObject.h"
#include "Emberfall/Gameplay/World/Cover/CoverSettings.h"
#include "Emberfall/Gameplay/World/Cover/CoverSpatialGrid.h"

#include "DrawDebugHelpers.h"
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

#if ENABLE_DRAW_DEBUG
    if (GetDefault<UCoverSettings>()->bDrawDebugGrid)
    {
        DrawDebugCells(-1.0f);
        DrawDebugFootprints(-1.0f);
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

#if ENABLE_DRAW_DEBUG
void UCoverSubsystem::DrawDebugCells(float Duration) const
{
    if (!SpatialGrid)
    {
        return;
    }

    const float CellSize = SpatialGrid->GetCellSize();
    const float GridHeight = GetDefault<UCoverSettings>()->DebugGridPlaneZ;
    const FVector HalfExtent(CellSize * 0.5f, CellSize * 0.5f, 0.0f);

    for (const TPair<FIntPoint, TArray<TWeakObjectPtr<ACoverObject>>>& CellEntry : SpatialGrid->GetCells())
    {
        FString Label = FString::Printf(TEXT("Cell (%d, %d): %d"),
            CellEntry.Key.X, CellEntry.Key.Y, CellEntry.Value.Num());

        for (const TWeakObjectPtr<ACoverObject>& WeakObject : CellEntry.Value)
        {
            if (const ACoverObject* CoverObject = WeakObject.Get())
            {
                Label += FString::Printf(TEXT("\n%s"), *CoverObject->GetActorNameOrLabel());
            }
        }

        const FVector CellCenter(
            (CellEntry.Key.X + 0.5f) * CellSize,
            (CellEntry.Key.Y + 0.5f) * CellSize,
            GridHeight);

        DrawDebugBox(GetWorld(), CellCenter, HalfExtent, FColor::Yellow, Duration < 0.0f, Duration);
        DrawDebugString(GetWorld(), CellCenter + FVector(0.0f, 0.0f, 50.0f), Label,
            nullptr, FColor::Yellow, Duration, true, 1.2f);
    }
}

void UCoverSubsystem::DrawDebugFootprints(float Duration) const
{
    const UCoverSettings* Settings = GetDefault<UCoverSettings>();

    for (const TObjectPtr<ACoverObject>& CoverObject : CoverObjects)
    {
        TArray<FVector> Corners;
        if (!CoverObject || !CoverObject->GetFootprintCorners(Corners))
        {
            continue;
        }

        FVector Center = FVector::ZeroVector;
        for (const FVector& Corner : Corners)
        {
            Center += Corner;
        }
        Center /= Corners.Num();

        for (FVector& Corner : Corners)
        {
            const FVector OutwardDirection = (Corner - Center).GetSafeNormal2D();
            Corner += OutwardDirection * Settings->DebugFootprintOffsetXY;
            Corner.Z += Settings->DebugFootprintOffsetZ;
        }

        for (int32 CornerIndex = 0; CornerIndex < Corners.Num(); ++CornerIndex)
        {
            const FVector& Start = Corners[CornerIndex];
            const FVector& End = Corners[(CornerIndex + 1) % Corners.Num()];
            DrawDebugLine(GetWorld(), Start, End, FColor::Blue, Duration < 0.0f, Duration, 0, 4.0f);
        }
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