// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"

#include "EmberfallPlayerController.generated.h"

class UInputAction;
class UInputMappingContext;
class USelectionComponent;
struct FInputActionValue;


/**
 * @brief Player controller for the top-down view; owns the input bindings and forwards them to its components.
 */
UCLASS()
class EMBERFALL_API AEmberfallPlayerController : public APlayerController
{
	GENERATED_BODY()

public:
	/** @brief Default constructor. */
	AEmberfallPlayerController();

	/** @brief Returns the selection component; the HUD reads the drag state from it. */
	USelectionComponent* GetSelectionComponent() const { return SelectionComponent; }
	
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

	/** @brief Select button went down: starts a click or drag. */
	void OnSelectStarted(const FInputActionValue& Value);

	/** @brief Select button went up: finishes the click or drag. */
	void OnSelectCompleted(const FInputActionValue& Value);

	/** @brief Shift went down: further selections add to the current one. */
	void OnAddToSelectionStarted(const FInputActionValue& Value);

	/** @brief Shift went up: selections replace the current one again. */
	void OnAddToSelectionCompleted(const FInputActionValue& Value);
	
	//~=============================================================================
	// Commands

	/** @brief Orders the selected units to the cursor position. */
	void OnCommandStarted(const FInputActionValue& Value);

	//~=============================================================================
	// Camera

	/**
	 * @brief Pans the camera when the mouse is near a screen edge.
	 * @param MousePos Mouse position in viewport pixels.
	 */
	void UpdateEdgeScroll(const FVector2D& MousePos) const;
	
protected:
	//~=============================================================================
	// Input

	/** @brief Mapping context containing all gameplay actions. */
	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputMappingContext> GameplayMappingContext;

	/** @brief Left mouse button: click and drag select. */
	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputAction> SelectAction;

	/** @brief Shift: adds to the current selection instead of replacing it. */
	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputAction> AddToSelectionAction;

	/** @brief Right mouse button: orders the selected units to the cursor position. */
	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputAction> CommandAction;
	
	//~=============================================================================
	// Camera

	/** @brief Enables panning the camera at the screen edges. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera|EdgeScroll")
	bool bEdgeScrollEnabled{ true };

	/** @brief Distance to the screen edge in pixels at which scrolling starts. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera|EdgeScroll", meta = (ClampMin = "1"))
	float EdgeScrollMargin{ 20.0f };

	/** @brief How the mouse is locked to the viewport (@c LockAlways is needed for edge scrolling). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera|EdgeScroll")
	EMouseLockMode MouseLockMode{ EMouseLockMode::LockAlways };
	
private:
	//~=============================================================================
	// Selection

	/** @brief Hover, click and drag-box selection of player units. */
	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<USelectionComponent> SelectionComponent;
	
};