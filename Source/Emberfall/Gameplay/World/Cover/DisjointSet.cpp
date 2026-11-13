// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/DisjointSet.h"


FDisjointSet::FDisjointSet(int32 Count)
{
    Parents.SetNumUninitialized(Count);
    for (int32 Index = 0; Index < Count; ++Index)
    {
        Parents[Index] = Index;
    }
}

int32 FDisjointSet::Find(int32 Index)
{
    checkSlow(Parents.IsValidIndex(Index));

    // Path halving: every visited node jumps to its grandparent, keeping the trees flat.
    while (Parents[Index] != Index)
    {
        Parents[Index] = Parents[Parents[Index]];
        Index = Parents[Index];
    }
    return Index;
}

void FDisjointSet::Merge(int32 FirstIndex, int32 SecondIndex)
{
    Parents[Find(FirstIndex)] = Find(SecondIndex);
}