// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "SelectionDragState.h"
#include "Emberfall/Characters/Player/PlayerUnit.h"
#include "GameFramework/PlayerController.h"
#include "EmberfallPlayerController.generated.h"


struct FInputActionValue;
class APlayerUnit;
class UInputAction;
class UInputMappingContext;

/**
 * @brief Player controller for the top-down view; keeps the mouse cursor visible and usable.
 */
UCLASS()
class EMBERFALL_API AEmberfallPlayerController : public APlayerController
{
	GENERATED_BODY()

public:
	/** @brief Default constructor. */
	AEmberfallPlayerController();

	/** @brief Returns the select press/drag state; the HUD reads it to draw the selection box. */
	const FSelectionDragState& GetSelectionDragState() const { return SelectionDragState; }
	
protected:
	/** @brief Sets the input mode so game input and the visible cursor work together. */
	virtual void BeginPlay() override;
	
	/** @brief Binds @c SelectAction. */
	virtual void SetupInputComponent() override;
	
	/**
	 * @brief Updates hover, selection drag and edge scrolling each frame.
	 * @param DeltaSeconds Seconds since the last frame.
	 */
	virtual void Tick(float DeltaSeconds) override;

private:
	//~=============================================================================
	// Selection
	
	/** @brief Traces under the cursor and updates @c HoveredUnit. */
	void UpdateHover();
	
	/**
	 * @brief Hovers all units inside the drag box and un-hovers those that left it.
	 * @param MousePos Mouse position in viewport pixels.
	 */
	void UpdateDragHover(const FVector2D& MousePos);
	
	/**
	 * @brief Begins tracking the press in @c SelectionDragState.
	 * @param Value Unused.
	 */
	void OnSelectStarted(const FInputActionValue& Value);
	
	/**
     * @brief Selects @c HoveredUnit, or clears the selection when clicking empty space.
     * @param Value Unused.
     */
    void OnSelectCompleted(const FInputActionValue& Value);
	
	/** @brief Deselects all units in @c SelectedUnits. */
	void ClearSelection();
	
	/**
	 * @brief Collects all player units whose screen bounds touch the given rectangle.
	 * @param A First corner in viewport pixels.
	 * @param B Opposite corner in viewport pixels.
	 * @param OutUnits Receives the units found (cleared first).
	 */
	void GetUnitsInRect(const FVector2D& A, const FVector2D& B, TArray<APlayerUnit*>& OutUnits);
	
	//~=============================================================================
	// Camera
	
	/**
	 * @brief Pans the camera when the mouse is near a screen edge.
	 * @param MousePos Mouse position in viewport pixels.
	 */
	void UpdateEdgeScroll(const FVector2D& MousePos) const;
	
protected:
    /** @brief Enables panning the camera at the screen edges. */
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera|EdgeScroll")
    bool bEdgeScrollEnabled{ true };

    /** @brief Distance to the screen edge in pixels at which scrolling starts. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera|EdgeScroll", meta = (ClampMin = "1"))
	float EdgeScrollMargin{ 20.0f };
	
	/** @brief Locks the mouse to the viewport (needed for edge scrolling). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	EMouseLockMode MouseLockMode{ EMouseLockMode::LockAlways };
	
	/** @brief Mapping context containing @c SelectAction. */
	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputMappingContext> GameplayMappingContext;

	/** @brief Left mouse button: click and drag select. */
	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputAction> SelectAction;
	
	/** @brief Distance in pixels the mouse must move before a press counts as a drag. */
	UPROPERTY(EditDefaultsOnly, Category = "Input", meta = (ClampMin = "1"))
	float DragThreshold{ 8.0f };
	
private:
	/** @brief Unit currently under the cursor. */
	UPROPERTY()
	TObjectPtr<APlayerUnit> HoveredUnit{ nullptr };

	/** @brief Units currently hovered by the drag box. */
	UPROPERTY()
	TArray<TObjectPtr<APlayerUnit>> DragHoveredUnits;
	
	
	/** @brief Units in the current selection. */
	UPROPERTY()
	TArray<TObjectPtr<APlayerUnit>> SelectedUnits;
	
private:
	/** @brief Tracks the select button press to tell a click from a drag-box selection. */
	FSelectionDragState SelectionDragState;
};