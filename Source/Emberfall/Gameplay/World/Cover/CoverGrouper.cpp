// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverGrouper.h"
#include "Emberfall/Gameplay/World/Cover/CoverGeometry.h"
#include "Emberfall/Gameplay/World/Cover/CoverObject.h"
#include "Emberfall/Gameplay/World/Cover/CoverSettings.h"
#include "Emberfall/Gameplay/World/Cover/CoverSpatialGrid.h"
#include "Emberfall/Gameplay/World/Cover/DisjointSet.h"


FCoverGrouper::FCoverGrouper(const FCoverSpatialGrid& InGrid, const UCoverSettings& InSettings)
    : Grid(InGrid)
    , Settings(InSettings)
{
}

void FCoverGrouper::Build(const TArray<ACoverObject*>& Objects, TArray<FCoverGroup>& OutGroups) const
{
    OutGroups.Reset();

    //
    // Index every object, the disjoint set works on indices only
    //
    TMap<ACoverObject*, int32> IndexOfObject;
    IndexOfObject.Reserve(Objects.Num());
    for (int32 ObjectIndex = 0; ObjectIndex < Objects.Num(); ++ObjectIndex)
    {
        IndexOfObject.Add(Objects[ObjectIndex], ObjectIndex);
    }

    //
    // Merge every candidate pair whose footprints are closer than MergeRadius
    //
    FDisjointSet Sets(Objects.Num());

    const double MergeRadius = FMath::Max(Settings.MergeRadius, 0.0f);
    const double MergeRadiusSquared = MergeRadius * MergeRadius;

    TArray<TPair<ACoverObject*, ACoverObject*>> CandidatePairs;
    Grid.GetCandidatePairs(CandidatePairs);
    for (const TPair<ACoverObject*, ACoverObject*>& CandidatePair : CandidatePairs)
    {
        const int32* FirstIndex = IndexOfObject.Find(CandidatePair.Key);
        const int32* SecondIndex = IndexOfObject.Find(CandidatePair.Value);
        if (!FirstIndex || !SecondIndex)
        {
            continue;
        }

        TArray<FVector> FirstCorners;
        TArray<FVector> SecondCorners;
        if (!CandidatePair.Key->GetFootprintCorners(FirstCorners)
            || !CandidatePair.Value->GetFootprintCorners(SecondCorners))
        {
            continue;
        }

        if (FCoverGeometry::DistanceSquared2D(FirstCorners, SecondCorners) <= MergeRadiusSquared)
        {
            Sets.Merge(*FirstIndex, *SecondIndex);
        }
    }

    //
    // Turn each set root into one group
    //
    TMap<int32, int32> GroupIndexOfRoot;
    for (int32 ObjectIndex = 0; ObjectIndex < Objects.Num(); ++ObjectIndex)
    {
        const int32 Root = Sets.Find(ObjectIndex);
        int32* GroupIndex = GroupIndexOfRoot.Find(Root);
        if (!GroupIndex)
        {
            FCoverGroup& NewGroup = OutGroups.Emplace_GetRef(OutGroups.Num());
            GroupIndex = &GroupIndexOfRoot.Add(Root, NewGroup.GetGroupId());
        }
        OutGroups[*GroupIndex].AddMember(Objects[ObjectIndex]);
    }
}