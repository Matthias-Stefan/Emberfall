// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"


/** @brief Phase of the cover state machine. */
UENUM(BlueprintType)
enum class ECoverState : uint8
{
    /** @brief Not in cover. */
    None,
    /** @brief Sliding onto the cover line. */
    Docking,
    /** @brief Docked, can move along the cover line. */
    InCover
};

/** @brief Data of the slide onto the cover line. */
struct FCoverDockData
{
    /** @brief Progress of the dock slide from 0 to 1. */
    float Alpha{0.f};

    /** @brief Unit location when the dock slide started. */
    FVector StartLocation{FVector::ZeroVector};

    /** @brief Point on the cover line the unit slides to. */
    FVector TargetLocation{FVector::ZeroVector};

    /** @brief Unit rotation when the dock slide started. */
    FQuat StartRotation{FQuat::Identity};

    /** @brief Rotation facing the wall, reached at the end of the dock slide. */
    FQuat TargetRotation{FQuat::Identity};

    /** @brief Relative mesh location before entering cover, restored on leaving. */
    FVector MeshStartLocation{FVector::ZeroVector};
};
