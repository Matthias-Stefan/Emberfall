// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "Emberfall/PlayerController/Selection/SelectionDragState.h"

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"

#include "SelectionComponent.generated.h"

class APlayerController;
class APlayerUnit;


/**
 * @brief Hover, click and drag-box selection of player units; input is forwarded by the controller.
 */
UCLASS(ClassGroup=(Emberfall))
class EMBERFALL_API USelectionComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	USelectionComponent();

	/** @brief Traces under the cursor and updates the hovered unit. Skipped while dragging. */
	void UpdateHover();

	/**
	 * @brief Updates the drag state and hovers all units inside the drag box.
	 * @param MousePos Mouse position in viewport pixels.
	 */
	void UpdateDrag(const FVector2D& MousePos);

	/**
	 * @brief Select button went down: starts tracking a click or drag.
	 * @param MousePos Mouse position in viewport pixels.
	 */
	void BeginPress(const FVector2D& MousePos);

	/**
	 * @brief Select button went up: box-selects after a drag, otherwise click-selects the hovered unit.
	 * @param MousePos Mouse position in viewport pixels.
	 */
	void EndPress(const FVector2D& MousePos);

	/** @brief Aborts a running press without selecting anything, e.g. when released outside the viewport. */
	void CancelPress();
	
	/**
	 * @brief Sets whether selections add to the current one instead of replacing it.
	 * @param bEnabled @c true while the add key (Shift) is held.
	 */
	void SetAddMode(bool bEnabled) { bAddToSelection = bEnabled; }

	/** @brief Returns the units in the current selection. */
	const TArray<TObjectPtr<APlayerUnit>>& GetSelectedUnits() const { return SelectedUnits; }

	/** @brief Returns the select press/drag state; the HUD reads it to draw the selection box. */
	const FSelectionDragState& GetDragState() const { return DragState; }

protected:
	virtual void BeginPlay() override;

private:
	/** @brief Deselects all units in @c SelectedUnits. */
	void ClearSelection();

	/**
	 * @brief Collects all player units whose screen position lies inside the given rectangle.
	 * @param A First corner in viewport pixels.
	 * @param B Opposite corner in viewport pixels.
	 * @param OutUnits Receives the units found (cleared first).
	 */
	void GetUnitsInRect(const FVector2D& A, const FVector2D& B, TArray<APlayerUnit*>& OutUnits) const;

	/** @brief Distance in pixels the mouse must move before a press counts as a drag. */
	UPROPERTY(EditDefaultsOnly, Category = "Selection", meta = (ClampMin = "1"))
	float DragThreshold{ 8.0f };

	/** @brief Controller that owns this component, cached in @c BeginPlay. */
	UPROPERTY()
	TObjectPtr<APlayerController> OwnerController{ nullptr };

	/** @brief Unit currently under the cursor. */
	UPROPERTY()
	TObjectPtr<APlayerUnit> HoveredUnit{ nullptr };

	/** @brief Units currently hovered by the drag box. */
	UPROPERTY()
	TArray<TObjectPtr<APlayerUnit>> DragHoveredUnits;

	/** @brief Units in the current selection. */
	UPROPERTY()
	TArray<TObjectPtr<APlayerUnit>> SelectedUnits;

	/** @brief Tracks the select button press to tell a click from a drag-box selection. */
	FSelectionDragState DragState;

	/** @brief Selections add to the current one instead of replacing it. */
	bool bAddToSelection{ false };
};
