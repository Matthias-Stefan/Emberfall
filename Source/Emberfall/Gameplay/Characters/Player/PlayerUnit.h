// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "Emberfall/Gameplay/Characters/Player/PlayerUnitTypes.h"

#include "CoreMinimal.h"
#include "GameFramework/Character.h"

#include "PlayerUnit.generated.h"

class USplineComponent;


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

	/** @brief */
	virtual void Tick(float DeltaTime) override;
	
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

	//~=============================================================================
	// Cover
	
	/**
	 * @brief Projects a move target onto the cover line the unit is docked to.
	 * @param Target Requested world location.
	 * @return @c Target projected onto the cover line, the current location while docking,
	 *         or @c Target unchanged if the unit is not in cover.
	 */
	FVector ConstrainToCover(const FVector& Target) const;
	
	/**
	 * @brief Traces forward on the @c ECC_Cover channel and enters cover if a @c ACoverObject is in reach.
	 * @return @c true if cover was entered.
	 */
	UFUNCTION(BlueprintCallable, Category = "Cover")
	bool TryEnterCover();
	
	/**
	 * @brief Enters or leaves cover.
	 * @param bInCover @c true to enter cover, @c false to leave it.
	 */
	UFUNCTION(BlueprintCallable, Category = "Cover")
	void SetInCover(bool bInCover);

	/**
	 * @brief Returns whether the unit is currently in cover.
	 * @return @c true while the unit is in cover.
	 */
	UFUNCTION(BlueprintPure, Category = "Cover")
	bool IsInCover() const { return bIsInCover; }
	
protected:
	/**
	 * @brief Fired when @c SelectionState changes. Implement the visual feedback in Blueprint.
	 * @param NewState The new @c EPlayerUnitTypes selection state.
	 */
	UFUNCTION(BlueprintImplementableEvent, Category = "Selection")
	void OnSelectionStateChanged(EPlayerUnitTypes NewState);

protected:
	/** @brief Reach of the cover trace in cm, measured from the unit center along its forward vector. */
	UPROPERTY(EditDefaultsOnly, Category = "Cover")
	float CoverTraceDistance = 150.f;
	
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

	/** @brief @c true while the unit is in cover, read by the AnimBP. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Cover", meta = (AllowPrivateAccess = "true"))
	bool bIsInCover = false;
	
// Cover
private:
	/** @brief Spline of the cover the unit is docked to. */
	TWeakObjectPtr<USplineComponent> CoverSpline;

	/** @brief Dock normal of the current cover, points away from the wall. */
	FVector CoverNormal = FVector::ZeroVector;

	/** @brief @c true while the unit slides onto the cover line after entering. */
	bool bIsDocking = false;

	/** @brief Progress of the dock slide from 0 to 1. */
	float DockAlpha = 0.f;

	/** @brief Unit location when the dock slide started. */
	FVector DockStartLocation = FVector::ZeroVector;

	/** @brief Point on the cover line the unit slides to. */
	FVector DockTargetLocation = FVector::ZeroVector;

	/** @brief Unit rotation when the dock slide started. */
	FQuat DockStartRotation = FQuat::Identity;

	/** @brief Rotation facing the wall, reached at the end of the dock slide. */
	FQuat DockTargetRotation = FQuat::Identity;

	/** @brief Duration in seconds of the slide onto the cover line. */
	UPROPERTY(EditDefaultsOnly, Category = "Cover")
	float DockDuration = 0.25f;	
};
