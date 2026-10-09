// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "Emberfall/Gameplay/Characters/Player/PlayerUnitTypes.h"

#include "CoreMinimal.h"
#include "GameFramework/Character.h"

#include "PlayerUnit.generated.h"

class UCoverComponent;


/**
 * @brief Controllable character of the player. Shows hover and selection state through
 *        @c OnSelectionStateChanged; movement is driven by an AI controller.
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
    
    //~=============================================================================
    // Selection

    /**
     * @brief Sets the hover flag and refreshes the selection state.
     * @param bInHovered @c true while the cursor is over the unit.
     */
    void SetHovered(bool bInHovered);

    /**
     * @brief Sets the selected flag and refreshes the selection state.
     * @param bInSelected @c true while the unit is part of the current selection.
     */
    void SetSelected(bool bInSelected);

    /**
     * @brief Returns the current selection state (@c Selected wins over @c Hovered).
     * @return Current @c EPlayerUnitTypes selection state.
     */
    UFUNCTION(BlueprintPure, Category = "Selection")
    EPlayerUnitTypes GetSelectionState() const { return SelectionState; }

    /**
     * @brief Returns the cover component of the unit.
     * @return The @c UCoverComponent, never @c nullptr after construction.
     */
    UFUNCTION(BlueprintPure, Category = "Cover")
    UCoverComponent* GetCoverComponent() const { return CoverComponent; }
    
protected:
    /**
     * @brief Fired when @c SelectionState changes. Implement the visual feedback in Blueprint.
     * @param NewState The new @c EPlayerUnitTypes selection state.
     */
    UFUNCTION(BlueprintImplementableEvent, Category = "Selection")
    void OnSelectionStateChanged(EPlayerUnitTypes NewState);

private:
    /** @brief Derives @c SelectionState from @c bHovered / @c bSelected and fires @c OnSelectionStateChanged on change. */
    void UpdateSelectionState();

private:
    /** @brief Cursor is over the unit. */
    bool bHovered = false;

    /** @brief Unit is part of the current selection. */
    bool bSelected = false;

    /** @brief Derived from @c bHovered / @c bSelected, where @c Selected wins over @c Hovered. */
    EPlayerUnitTypes SelectionState = EPlayerUnitTypes::None;
    
    /** @brief Handles entering, leaving and moving along cover. */
    UPROPERTY(VisibleAnywhere, Category = "Components")
    TObjectPtr<UCoverComponent> CoverComponent;
};
