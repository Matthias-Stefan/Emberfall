// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"

#include "EmberfallHUD.generated.h"

class APlayerUnit;


/**
 * @brief HUD that draws the drag-selection box on screen.
 *        Reads the drag state from @c AEmberfallPlayerController; the box colors are tuned in Blueprint.
 */
UCLASS()
class EMBERFALL_API AEmberfallHUD : public AHUD
{
	GENERATED_BODY()

protected:
	/** @brief Draws the selection box while a drag is in progress. */
	virtual void DrawHUD() override;
	
protected:
	/** @brief Set after the missing-controller error was logged, so it appears only once. */
	bool bLoggedMissingController{ false };
};
