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
	/** @brief Fill color of the selection box. */
	UPROPERTY(EditDefaultsOnly, Category = "Selection")
	FLinearColor BoxFillColor{ 0.2f, 0.6f, 1.0f, 0.15f };

	/** @brief Border color of the selection box. */
	UPROPERTY(EditDefaultsOnly, Category = "Selection")
	FLinearColor BoxBorderColor{ 0.2f, 0.6f, 1.0f, 0.9f };

	/** @brief Border thickness in pixels. */
	UPROPERTY(EditDefaultsOnly, Category = "Selection", meta = (ClampMin = "1"))
	float BoxBorderThickness{ 1.0f };
};
