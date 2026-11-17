// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "Emberfall/Gameplay/Characters/Player/PlayerUnitTypes.h"

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"

#include "PlayerUnitSelectionComponent.generated.h"


/**
 * @brief Broadcasts when the derived selection state of the owning unit changes.
 */
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnPlayerUnitSelectionStateChanged, EPlayerUnitTypes, NewState);


/**
 * @brief Holds the hover and selection state of an @c APlayerUnit and notifies listeners about changes.
 */
UCLASS(ClassGroup = (Emberfall), meta = (BlueprintSpawnableComponent))
class EMBERFALL_API UPlayerUnitSelectionComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPlayerUnitSelectionComponent();

    /**
     * @brief Sets the hover flag and refreshes the selection state.
     * @param bInHovered is @c true while the cursor is over the unit.
     */
    void SetHovered(bool bInHovered);

    /**
     * @brief Sets the selected flag and refreshes the selection state.
     * @param bInSelected is @c true while the unit is part of the current selection.
     */
    void SetSelected(bool bInSelected);

    /**
     * @brief Returns the current selection state, where @c Selected wins over @c Hovered.
     * @return Current @c EPlayerUnitTypes selection state.
     */
    UFUNCTION(BlueprintPure, Category = "Selection")
    EPlayerUnitTypes GetSelectionState() const { return SelectionState; }

    /** @brief Fired when @c SelectionState changes; bind the visual feedback to it. */
    UPROPERTY(BlueprintAssignable, Category = "Selection")
    FOnPlayerUnitSelectionStateChanged OnSelectionStateChanged;

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
};