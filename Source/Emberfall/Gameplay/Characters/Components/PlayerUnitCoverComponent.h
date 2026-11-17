// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"

#include "PlayerUnitCoverComponent.generated.h"


/**
 * @brief Manages the cover state of an @c APlayerUnit.
 */
UCLASS(ClassGroup = (Emberfall), meta = (BlueprintSpawnableComponent))
class EMBERFALL_API UPlayerUnitCoverComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPlayerUnitCoverComponent();

    /**
     * @brief Tries to take cover at the nearest suitable cover object.
     * @return @c true if the unit entered cover, otherwise @c false.
     */
    bool TryEnterCover();

    /**
     * @brief Leaves the current cover and clears @c bIsInCover.
     */
    void LeaveCover();

    /**
     * @brief Tests whether the owning unit is in cover.
     * @return @c true if the unit is in cover, otherwise @c false.
     */
    UFUNCTION(BlueprintPure, Category = "Cover")
    bool IsInCover() const { return bIsInCover; }

private:
    /** @brief Unit is currently in cover. */
    bool bIsInCover = false;
};