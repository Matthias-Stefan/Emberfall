// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"


/**
 * @brief Union-find over the indices @c 0 to @c Count-1.
 */
class EMBERFALL_API FDisjointSet
{
public:
    /**
     * @brief Creates a set where every index is its own group.
     * @param Count is the number of elements.
     */
    explicit FDisjointSet(int32 Count);

    /**
     * @brief Finds the representative of the group containing an element.
     * @param Index is the element to look up.
     * @return Root index of the group containing @c Index.
     */
    int32 Find(int32 Index);

    /**
     * @brief Merges the groups of two elements.
     * @param FirstIndex is the first element.
     * @param SecondIndex is the second element.
     */
    void Merge(int32 FirstIndex, int32 SecondIndex);

private:
    /** @brief Parent index per element, a root points to itself. */
    TArray<int32> Parents;
};