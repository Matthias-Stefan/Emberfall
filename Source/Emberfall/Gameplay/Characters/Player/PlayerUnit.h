// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"

#include "PlayerUnit.generated.h"

class UPlayerUnitCoverComponent;
class UPlayerUnitSelectionComponent;


/**
 * @brief Controllable character of the player; selection and cover state live in their own components,
 *        movement is driven by an AI controller.
 */
UCLASS()
class EMBERFALL_API APlayerUnit : public ACharacter
{
    GENERATED_BODY()

public:
    APlayerUnit();

    /**
     * @brief Orders the unit to a world location; in cover the target is projected onto the cover line and the navmesh is skipped.
     * @param Target Requested world location.
     */
    void MoveToTarget(const FVector& Target);

    /**
     * @brief Returns the selection component that holds the hover and selection state.
     * @return Selection component of this unit.
     */
    UPlayerUnitSelectionComponent* GetSelectionComponent() const { return SelectionComponent; }

    /**
     * @brief Returns the cover component that holds the cover state.
     * @return Cover component of this unit.
     */
    UFUNCTION(BlueprintPure, Category = "Cover")
    UPlayerUnitCoverComponent* GetCoverComponent() const { return CoverComponent; }

private:
    /** @brief Hover and selection state of this unit. */
    UPROPERTY(VisibleAnywhere, Category = "Components")
    TObjectPtr<UPlayerUnitSelectionComponent> SelectionComponent;

    /** @brief Cover state and cover movement of this unit. */
    UPROPERTY(VisibleAnywhere, Category = "Components")
    TObjectPtr<UPlayerUnitCoverComponent> CoverComponent;
};