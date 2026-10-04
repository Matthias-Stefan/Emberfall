// Copyright (c) 2026 Emberfall. All Rights Reserved.


#include "EmberfallPlayerController.h"

AEmberfallPlayerController::AEmberfallPlayerController()
{
	bShowMouseCursor = true;
	DefaultMouseCursor = EMouseCursor::Default;
}

void AEmberfallPlayerController::BeginPlay()
{
	Super::BeginPlay();
	
	FInputModeGameAndUI InputMode;
	InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::LockAlways);
	InputMode.SetHideCursorDuringCapture(false);
	SetInputMode(InputMode);
}
