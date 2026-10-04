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
};