// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "SelectionSettings.generated.h"

/**
 * @brief Single source of truth for selection visuals (outline colors and drag box).
 */
UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "Selection"))
class EMBERFALL_API USelectionSettings : public UDeveloperSettings
{
	GENERATED_BODY()
	
public:
	USelectionSettings();

	/** @brief Fill color of the drag box: @c HoverColor with @c BoxFillAlpha. */
	FLinearColor GetBoxFillColor() const;

	/** @brief Border color of the drag box: @c HoverColor with @c BoxBorderAlpha. */
	FLinearColor GetBoxBorderColor() const;

	/** @brief Outline color of a hovered unit (stencil value 1). */
	UPROPERTY(Config, EditAnywhere, Category = "Colors")
	FLinearColor HoverColor;

	/** @brief Outline and drag box color of a selected unit (stencil value 2). */
	UPROPERTY(Config, EditAnywhere, Category = "Colors")
	FLinearColor SelectColor;

	/** @brief Opacity of the drag box fill. */
	UPROPERTY(Config, EditAnywhere, Category = "Drag Box", meta = (ClampMin = "0", ClampMax = "1"))
	float BoxFillAlpha{ 0.15f };

	/** @brief Opacity of the drag box border. */
	UPROPERTY(Config, EditAnywhere, Category = "Drag Box", meta = (ClampMin = "0", ClampMax = "1"))
	float BoxBorderAlpha{ 0.9f };

	/** @brief Border thickness of the drag box in pixels. */
	UPROPERTY(Config, EditAnywhere, Category = "Drag Box", meta = (ClampMin = "1"))
	float BoxBorderThickness{ 1.0f };

	/** @brief Collection the outline post process material reads its colors from. */
	UPROPERTY(Config, EditAnywhere, Category = "Material")
	TSoftObjectPtr<UMaterialParameterCollection> OutlineParameters;
};
