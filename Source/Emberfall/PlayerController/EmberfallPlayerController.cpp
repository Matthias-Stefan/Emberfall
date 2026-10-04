// Copyright (c) 2026 Emberfall. All Rights Reserved.


#include "EmberfallPlayerController.h"

#include "Emberfall/Camera/CameraPawn.h"

AEmberfallPlayerController::AEmberfallPlayerController()
{
	PrimaryActorTick.bCanEverTick = true;

	bShowMouseCursor = true;
	DefaultMouseCursor = EMouseCursor::Default;
}

void AEmberfallPlayerController::BeginPlay()
{
	Super::BeginPlay();

	UE_LOG(LogTemp, Warning, TEXT("EmberfallPlayerController BeginPlay, cursor=%d"), bShowMouseCursor);
	
	FInputModeGameAndUI InputMode;
	InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::LockAlways);
	InputMode.SetHideCursorDuringCapture(false);
	SetInputMode(InputMode);
}

void AEmberfallPlayerController::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	if (!bEdgeScrollEnabled)
	{
		return;
	}

	ACameraPawn* CameraPawn = Cast<ACameraPawn>(GetPawn());
	if (CameraPawn == nullptr)
	{
		return;
	}

	float MouseX = 0.0f;
	float MouseY = 0.0f;
	if (!GetMousePosition(MouseX, MouseY))
	{
		return;
	}

	int32 SizeX = 0;
	int32 SizeY = 0;
	GetViewportSize(SizeX, SizeY);

	// Screen Y grows downwards, so the top edge means "forward"
	FVector2D Input = FVector2D::ZeroVector;

	if (MouseX <= EdgeScrollMargin)
	{
		Input.X = -1.0f;
	}
	else if (MouseX >= SizeX - EdgeScrollMargin)
	{
		Input.X = 1.0f;
	}

	if (MouseY <= EdgeScrollMargin)
	{
		Input.Y = 1.0f;
	}
	else if (MouseY >= SizeY - EdgeScrollMargin)
	{
		Input.Y = -1.0f;
	}

	if (!Input.IsZero())
	{
		CameraPawn->AddPanInput(Input);
	}
}
