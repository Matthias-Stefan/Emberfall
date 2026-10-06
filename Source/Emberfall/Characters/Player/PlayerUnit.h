// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "Emberfall/Characters/Player/PlayerUnitTypes.h"

#include "CoreMinimal.h"
#include "GameFramework/Character.h"

#include "PlayerUnit.generated.h"


/**
 * @brief Controllable character of the player. Shows hover and selection state through
 *        @c OnSelectionStateChanged; movement is driven by an AI controller.
 */
UCLASS()
class EMBERFALL_API APlayerUnit : public ACharacter
{
	GENERATED_BODY()

public:
	// Sets default values for this character's properties
	APlayerUnit();

	/** @brief Sets the hover flag and refreshes the selection state. */
	void SetHovered(bool bInHovered);

	/** @brief Sets the selected flag and refreshes the selection state. */
	void SetSelected(bool bInSelected);

	/** @brief Returns the current selection state (@c Selected wins over @c Hovered). */
	UFUNCTION(BlueprintPure, Category = "Selection")
	EPlayerUnitTypes GetSelectionState() const { return SelectionState; }
	
protected:
	/** @brief Fired when @c SelectionState changes. Implement the visual feedback in Blueprint. */
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
};
