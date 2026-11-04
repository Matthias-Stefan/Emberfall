// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"


/**
 * @brief Ordered list of points that forms one closed outline around cover, derived data and never the source of truth.
 */
struct FCoverLoop
{
    /** @brief Corner points of the loop in world space in cm, in walking order, the last point connects back to the first. */
    TArray<FVector> Points;
};