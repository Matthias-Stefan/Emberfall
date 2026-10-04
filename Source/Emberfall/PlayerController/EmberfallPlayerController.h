// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "EmberfallPlayerController.generated.h"

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

protected:
	/** @brief Sets the input mode so game input and the visible cursor work together. */
	virtual void BeginPlay() override;
	
	/**
     * @brief Scrolls the camera when the mouse is near a screen edge.
     * @param DeltaSeconds Seconds since the last frame.
     */
    virtual void Tick(float DeltaSeconds) override;

protected:
    /** @brief Enables panning the camera at the screen edges. */
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera|EdgeScroll")
    bool bEdgeScrollEnabled{ true };

    /** @brief Distance to the screen edge in pixels at which scrolling starts. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera|EdgeScroll", meta = (ClampMin = "1"))
	float EdgeScrollMargin{ 20.0f };
};