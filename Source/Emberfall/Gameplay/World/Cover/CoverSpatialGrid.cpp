// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverSpatialGrid.h"

#include "Emberfall/Gameplay/World/Cover/CoverObject.h"
#include "Emberfall/Gameplay/World/Cover/CoverSettings.h"


FCoverSpatialGrid::FCoverSpatialGrid(const UCoverSettings& InSettings)
    : Settings(InSettings)
{
}

bool FCoverSpatialGrid::Insert(ACoverObject* CoverObject)
{
    if (!IsValid(CoverObject))
    {
        return false;
    }

    const TWeakObjectPtr<ACoverObject> WeakObject(CoverObject);
    if (OccupiedCells.Contains(WeakObject))
    {
        return false;
    }

    TArray<FIntPoint> TouchedCells;
    if (!ComputeOccupiedCells(*CoverObject, TouchedCells))
    {
        return false;
    }

    for (const FIntPoint& Cell : TouchedCells)
    {
        Cells.FindOrAdd(Cell).Add(WeakObject);
    }
    OccupiedCells.Add(WeakObject, MoveTemp(TouchedCells));
    return true;
}

bool FCoverSpatialGrid::Remove(ACoverObject* CoverObject)
{
    const TWeakObjectPtr<ACoverObject> WeakObject(CoverObject);

    TArray<FIntPoint> TouchedCells;
    if (!OccupiedCells.RemoveAndCopyValue(WeakObject, TouchedCells))
    {
        return false;
    }

    for (const FIntPoint& Cell : TouchedCells)
    {
        TArray<TWeakObjectPtr<ACoverObject>>* CellObjects = Cells.Find(Cell);
        if (!CellObjects)
        {
            continue;
        }

        CellObjects->RemoveSingleSwap(WeakObject);
        if (CellObjects->IsEmpty())
        {
            Cells.Remove(Cell);
        }
    }
    return true;
}

void FCoverSpatialGrid::Query(const FVector& Position, float Radius, TArray<ACoverObject*>& OutCoverObjects) const
{
    const FIntPoint MinCell = WorldToCell(Position - FVector(Radius, Radius, 0.0f));
    const FIntPoint MaxCell = WorldToCell(Position + FVector(Radius, Radius, 0.0f));

    TSet<ACoverObject*> UniqueObjects;
    for (int32 CellX = MinCell.X; CellX <= MaxCell.X; ++CellX)
    {
        for (int32 CellY = MinCell.Y; CellY <= MaxCell.Y; ++CellY)
        {
            const TArray<TWeakObjectPtr<ACoverObject>>* CellObjects = Cells.Find(FIntPoint(CellX, CellY));
            if (!CellObjects)
            {
                continue;
            }

            for (const TWeakObjectPtr<ACoverObject>& WeakObject : *CellObjects)
            {
                if (ACoverObject* CoverObject = WeakObject.Get())
                {
                    UniqueObjects.Add(CoverObject);
                }
            }
        }
    }
    OutCoverObjects = UniqueObjects.Array();
}

void FCoverSpatialGrid::GetCandidatePairs(TArray<TPair<ACoverObject*, ACoverObject*>>& OutPairs) const
{
    OutPairs.Reset();
    TSet<uint64> SeenPairKeys;

    for (const TPair<FIntPoint, TArray<TWeakObjectPtr<ACoverObject>>>& CellEntry : Cells)
    {
        const TArray<TWeakObjectPtr<ACoverObject>>& Members = CellEntry.Value;
        for (int32 FirstIndex = 0; FirstIndex < Members.Num(); ++FirstIndex)
        {
            ACoverObject* FirstObject = Members[FirstIndex].Get();
            if (!FirstObject)
            {
                continue;
            }

            for (int32 SecondIndex = FirstIndex + 1; SecondIndex < Members.Num(); ++SecondIndex)
            {
                ACoverObject* SecondObject = Members[SecondIndex].Get();
                if (!SecondObject)
                {
                    continue;
                }

                // Order-independent key, so the pair (A, B) and (B, A) collapse into one entry.
                const uint32 FirstId = FirstObject->GetUniqueID();
                const uint32 SecondId = SecondObject->GetUniqueID();
                const uint64 PairKey = (static_cast<uint64>(FMath::Min(FirstId, SecondId)) << 32)
                                     | FMath::Max(FirstId, SecondId);

                bool bAlreadySeen = false;
                SeenPairKeys.Add(PairKey, &bAlreadySeen);
                if (!bAlreadySeen)
                {
                    OutPairs.Emplace(FirstObject, SecondObject);
                }
            }
        }
    }
}

void FCoverSpatialGrid::Empty()
{
    Cells.Empty();
    OccupiedCells.Empty();
}

float FCoverSpatialGrid::GetCellSize() const
{
    return FMath::Max(Settings.CellSize, 1.0f);
}

FIntPoint FCoverSpatialGrid::WorldToCell(const FVector& WorldPosition) const
{
    const float CellSize = GetCellSize();
    return FIntPoint(
        FMath::FloorToInt(WorldPosition.X / CellSize),
        FMath::FloorToInt(WorldPosition.Y / CellSize));
}

bool FCoverSpatialGrid::ComputeOccupiedCells(const ACoverObject& CoverObject, TArray<FIntPoint>& OutCells) const
{
    TArray<FVector> Corners;
    if (!CoverObject.GetFootprintCorners(Corners))
    {
        return false;
    }

    const float MergeRadius = GetMergeRadius();

    FVector2D MinCorner(Corners[0].X, Corners[0].Y);
    FVector2D MaxCorner = MinCorner;
    for (const FVector& Corner : Corners)
    {
        MinCorner.X = FMath::Min(MinCorner.X, Corner.X);
        MinCorner.Y = FMath::Min(MinCorner.Y, Corner.Y);
        MaxCorner.X = FMath::Max(MaxCorner.X, Corner.X);
        MaxCorner.Y = FMath::Max(MaxCorner.Y, Corner.Y);
    }

    const FIntPoint MinCell = WorldToCell(FVector(MinCorner.X - MergeRadius, MinCorner.Y - MergeRadius, 0.0f));
    const FIntPoint MaxCell = WorldToCell(FVector(MaxCorner.X + MergeRadius, MaxCorner.Y + MergeRadius, 0.0f));

    OutCells.Reset();
    for (int32 CellX = MinCell.X; CellX <= MaxCell.X; ++CellX)
    {
        for (int32 CellY = MinCell.Y; CellY <= MaxCell.Y; ++CellY)
        {
            OutCells.Add(FIntPoint(CellX, CellY));
        }
    }
    return true;
}

float FCoverSpatialGrid::GetMergeRadius() const
{
    return FMath::Max(Settings.MergeRadius, 0.0f);
}