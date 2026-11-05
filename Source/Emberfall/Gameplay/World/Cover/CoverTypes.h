// CoverTypes.h
// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

#include "CoverTypes.generated.h"


/**
 * @brief Sides of a cover object in its local space, combined as bit flags.
 */
UENUM(meta = (Bitflags, UseEnumValuesAsMaskValuesInEditor = "true"))
enum class ECoverSide : uint8
{
    /** @brief No side, only the empty mask. */
    None      = 0 UMETA(Hidden),

    /** @brief Side that faces along the local positive X axis. */
    PositiveX = 1 << 0,

    /** @brief Side that faces along the local negative X axis. */
    NegativeX = 1 << 1,

    /** @brief Side that faces along the local positive Y axis. */
    PositiveY = 1 << 2,

    /** @brief Side that faces along the local negative Y axis. */
    NegativeY = 1 << 3,

    /** @brief All four sides at once. */
    All       = PositiveX | NegativeX | PositiveY | NegativeY,
};
ENUM_CLASS_FLAGS(ECoverSide);

/**
 * @brief Ordered list of points that forms one outline around cover, derived data and never the source of truth.
 */
struct FCoverLoop
{
    /** @brief Corner points of the loop in world space in cm, in walking order, a closed loop connects the last point back to the first. */
    TArray<FVector> Points;
    
    /** @brief Whether the last point connects back to the first, @c false for a chain with a start and an end. */
    bool bIsClosed = true;
};

/**
 * @brief Straight piece of an edge between two points.
 */
struct FCoverEdgePiece
{
    /** @brief Start point of the piece in world space in cm. */
    FVector Start = FVector::ZeroVector;

    /** @brief End point of the piece in world space in cm. */
    FVector End = FVector::ZeroVector;

    /** @brief Index of the grown footprint this piece was cut from, @c INDEX_NONE if not set. */
    int32 SourceIndex = INDEX_NONE;
};

/**
 * @brief Footprint of one wall grown by the outline offset, with the data needed after the actor is out of sight.
 */
struct FCoverGrownFootprint
{
    /** @brief Corners of the grown footprint in world space in cm, all footprints share the same winding. */
    TArray<FVector> Corners;

    /** @brief Sides of the wall that take part in the cover path, copied from the wall. */
    ECoverSide EnabledSides = ECoverSide::All;

    /** @brief Direction of the wall's local positive X axis in the ground plane, normalized, mirrors with negative scale. */
    FVector2D AxisX = FVector2D(1.0, 0.0);

    /** @brief Direction of the wall's local positive Y axis in the ground plane, normalized, mirrors with negative scale. */
    FVector2D AxisY = FVector2D(0.0, 1.0);
};