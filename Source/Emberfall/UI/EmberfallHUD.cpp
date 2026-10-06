// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/UI/EmberfallHUD.h"
#include "Emberfall/EmberfallLog.h"
#include "Emberfall/PlayerController/EmberfallPlayerController.h"
#include "Emberfall/PlayerController/Selection/SelectionComponent.h"
#include "Emberfall/PlayerController/Selection/SelectionDragState.h"
#include "Emberfall/Settings/SelectionSettings.h"


void AEmberfallHUD::DrawHUD()
{
	Super::DrawHUD();
	
	//
	// Get drag state
	//
	
	const AEmberfallPlayerController* Controller = Cast<AEmberfallPlayerController>(GetOwningPlayerController());
	if (Controller == nullptr)
	{
		if (!bLoggedMissingController)
		{
			UE_LOG(LogEmberfall, Error, TEXT("%s: Owning controller is not an AEmberfallPlayerController."), *GetNameSafe(this));
			bLoggedMissingController = true;
		}
		return;
	}
	
	const USelectionComponent* Selection = Controller->GetSelectionComponent();
	if (Selection == nullptr)
	{
		return;
	}

	const FSelectionDragState& DragState = Selection->GetDragState();
	if (!DragState.IsDragging())
	{
		return;
	}

	float MouseX = 0.0f;
	float MouseY = 0.0f;
	if (!Controller->GetMousePosition(MouseX, MouseY))
	{
		return;
	}
	
	//
	// Build rect
	//
	
	const FVector2D Start = DragState.GetDragStart();
	const FVector2D Min{ FMath::Min(Start.X, MouseX), FMath::Min(Start.Y, MouseY) };
	const FVector2D Size{ FMath::Abs(MouseX - Start.X), FMath::Abs(MouseY - Start.Y) };
	
	//
	// Draw
	//
	
	const USelectionSettings* Settings = GetDefault<USelectionSettings>();
	DrawRect(Settings->GetBoxFillColor(), Min.X, Min.Y, Size.X, Size.Y);

	const FLinearColor BorderColor = Settings->GetBoxBorderColor();
	const float T = Settings->BoxBorderThickness;
	DrawRect(BorderColor, Min.X, Min.Y, Size.X, T);
	DrawRect(BorderColor, Min.X, Min.Y + Size.Y - T, Size.X, T);
	DrawRect(BorderColor, Min.X, Min.Y, T, Size.Y);
	DrawRect(BorderColor, Min.X + Size.X - T, Min.Y, T, Size.Y);
}
