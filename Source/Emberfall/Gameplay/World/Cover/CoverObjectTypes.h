// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"

#include "CoverObjectTypes.generated.h"


/** Trace channel "Cover", must match Project Settings. */
#define ECC_COVER ECC_GameTraceChannel1

/** @brief Height class of a cover object. */
UENUM(BlueprintType)
enum class ECoverHeight : uint8
{
    /** @brief Crouch behind it. */
    Low,
    /** @brief Stand and lean against it. */
    High
};

/** @brief Sides of a cover object as bit flags; the bit index equals the edge index of the outline loop. */
UENUM(BlueprintType, meta = (Bitflags, UseEnumValuesAsMaskValuesInEditor = "true"))
enum class ECoverSide : uint8
{
    /** @brief No side. */
    None = 0,
    /** @brief Edge 0, the negative Y face of the mesh. */
    NegativeY = 1 << 0,
    /** @brief Edge 1, the positive X end of the mesh. */
    PositiveX = 1 << 1,
    /** @brief Edge 2, the positive Y face of the mesh. */
    PositiveY = 1 << 2,
    /** @brief Edge 3, the negative X end of the mesh. */
    NegativeX = 1 << 3,
    /** @brief All four sides. */
    All = NegativeY | PositiveX | PositiveY | NegativeX
};
ENUM_CLASS_FLAGS(ECoverSide)

/** @brief Walkable run of consecutive active edges of a cover object. */
struct FCoverRun
{
    /** @brief World-space points of the run in walking direction; closed runs do not repeat the first point. */
    TArray<FVector> Points;
    /** @brief Outward normal per edge, one entry per edge between the points (plus the closing edge if @c bClosed). */
    TArray<FVector> EdgeNormals;
    /** @brief Outline edge index (0..3) per edge; the first entry identifies the run within its object. */
    TArray<int32> EdgeIds;
    /** @brief Run covers all four edges and wraps around. */
    bool bClosed{ false };
};