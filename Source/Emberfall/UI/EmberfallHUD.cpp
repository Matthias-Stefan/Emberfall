// Copyright (c) 2026 Emberfall. All Rights Reserved.


#include "EmberfallHUD.h"

#include "Emberfall/PlayerController/EmberfallPlayerController.h"


void AEmberfallHUD::DrawHUD()
{
	Super::DrawHUD();
	
	const AEmberfallPlayerController* Controller = Cast<AEmberfallPlayerController>(GetOwningPlayerController());
	if (Controller == nullptr)
	{
		// Log
		return;
	}
	
	const FSelectionDragState& DragState = Controller->GetSelectionDragState();
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
	
	const FVector2D Start = DragState.GetDragStart();
	const FVector2D Min{ FMath::Min(Start.X, MouseX), FMath::Min(Start.Y, MouseY) };
	const FVector2D Size{ FMath::Abs(MouseX - Start.X), FMath::Abs(MouseY - Start.Y) };
	
	DrawRect(BoxFillColor, Min.X, Min.Y, Size.X, Size.Y);
	
	const float T = BoxBorderThickness;
	DrawRect(BoxBorderColor, Min.X, Min.Y, Size.X, T);
	DrawRect(BoxBorderColor, Min.X, Min.Y + Size.Y - T, Size.X, T);
	DrawRect(BoxBorderColor, Min.X, Min.Y, T, Size.Y);
	DrawRect(BoxBorderColor, Min.X + Size.X - T, Min.Y, T, Size.Y);
}
