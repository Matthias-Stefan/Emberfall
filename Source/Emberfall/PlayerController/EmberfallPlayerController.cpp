// Copyright (c) 2026 Emberfall. All Rights Reserved.


#include "EmberfallPlayerController.h"

#include "EngineUtils.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "Emberfall/EmberfallLog.h"
#include "Emberfall/Camera/CameraPawn.h"
#include "Emberfall/Characters/Player/PlayerUnit.h"
#include "Emberfall/UI/EmberfallHUD.h"


AEmberfallPlayerController::AEmberfallPlayerController()
{
	PrimaryActorTick.bCanEverTick = true;

	bShowMouseCursor = true;
	DefaultMouseCursor = EMouseCursor::Default;
}

void AEmberfallPlayerController::BeginPlay()
{
	Super::BeginPlay();

	FInputModeGameAndUI InputMode;
	InputMode.SetLockMouseToViewportBehavior(MouseLockMode);
	InputMode.SetHideCursorDuringCapture(false);
	SetInputMode(InputMode);

	if (GameplayMappingContext == nullptr)
	{
		UE_LOG(LogEmberfall, Error, TEXT("%s: GameplayMappingContext is not set."), *GetNameSafe(this));
		return;
	}

	const ULocalPlayer* LocalPlayer = GetLocalPlayer();
	if (LocalPlayer == nullptr)
	{
		UE_LOG(LogEmberfall, Error, TEXT("%s: No LocalPlayer, cannot add mapping context."), *GetNameSafe(this));
		return;
	}

	UEnhancedInputLocalPlayerSubsystem* Subsystem =
		LocalPlayer->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>();
	if (Subsystem == nullptr)
	{
		UE_LOG(LogEmberfall, Error, TEXT("%s: EnhancedInput subsystem not found."), *GetNameSafe(this));
		return;
	}

	Subsystem->AddMappingContext(GameplayMappingContext, 0);
}

void AEmberfallPlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();

	UEnhancedInputComponent* EnhancedInput = Cast<UEnhancedInputComponent>(InputComponent);
	if (EnhancedInput == nullptr)
	{
		UE_LOG(LogEmberfall, Error, TEXT("%s: InputComponent is not a UEnhancedInputComponent."), *GetNameSafe(this));
		return;
	}

	if (SelectAction == nullptr)
	{
		UE_LOG(LogEmberfall, Error, TEXT("%s: SelectAction is not set."), *GetNameSafe(this));
		return;
	}

	EnhancedInput->BindAction(SelectAction, ETriggerEvent::Started, this, &AEmberfallPlayerController::OnSelectStarted);
	EnhancedInput->BindAction(SelectAction, ETriggerEvent::Completed, this, &AEmberfallPlayerController::OnSelectCompleted);
}

void AEmberfallPlayerController::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	//
	// Hover
	//
	
	if (!SelectionDragState.IsDragging())
	{
		UpdateHover();
	}
	
	//
	// Mouse position
	//

	float MouseX = 0.0f;
	float MouseY = 0.0f;
	if (!GetMousePosition(MouseX, MouseY))
	{
		return;
	}
	const FVector2D MousePos{ MouseX, MouseY };
	
	//
	// Selection drag
	//
	
	SelectionDragState.Update(MousePos, DragThreshold);
	
	//
	// Drag hover
	//

	if (SelectionDragState.IsDragging())
	{
		UpdateDragHover(MousePos);
	}
	
	//
	// Edge scrolling
	//

	if (bEdgeScrollEnabled)
	{
		UpdateEdgeScroll(MousePos);
	}
}

void AEmberfallPlayerController::UpdateHover()
{
	FHitResult Hit = {};
	GetHitResultUnderCursor(ECC_Visibility, false, Hit);
	APlayerUnit* NewHovered = Cast<APlayerUnit>(Hit.GetActor());
	
	if (NewHovered == HoveredUnit)
	{
		return;
	}
	
	if (HoveredUnit != nullptr)
	{
		HoveredUnit->SetHovered(false);
	}
	
	HoveredUnit = NewHovered;
	
	if (HoveredUnit != nullptr)
	{
		HoveredUnit->SetHovered(true);
	}
}

void AEmberfallPlayerController::UpdateDragHover(const FVector2D& MousePos)
{
	AEmberfallHUD* EmberfallHUD = Cast<AEmberfallHUD>(GetHUD());
	if (EmberfallHUD == nullptr)
	{
		return;
	}
	
	TArray<APlayerUnit*> InRect;
	GetUnitsInRect(SelectionDragState.GetDragStart(), MousePos, InRect);
	
	for (APlayerUnit* Unit : DragHoveredUnits)
	{
		if (!InRect.Contains(Unit))
		{
			Unit->SetHovered(false);
		}
	}
	
	for (APlayerUnit* Unit : InRect)
	{
		Unit->SetHovered(true);
	}

	DragHoveredUnits = InRect;
}

void AEmberfallPlayerController::OnSelectStarted(const FInputActionValue& Value)
{
	float MouseX{ 0.0f };
	float MouseY{ 0.0f };
	if (!GetMousePosition(MouseX, MouseY))
	{
		UE_LOG(LogEmberfall, Verbose, TEXT("%s: No mouse position, drag not started."), *GetNameSafe(this));
		return;
	}

	SelectionDragState.Begin(FVector2D{ MouseX, MouseY });
}

void AEmberfallPlayerController::OnSelectCompleted(const FInputActionValue& Value)
{
	const FVector2D DragStart = SelectionDragState.GetDragStart();
	float MouseX = 0.0f;
	float MouseY = 0.0f;
	GetMousePosition(MouseX, MouseY);
	
	const bool bWasDrag = SelectionDragState.Complete();
	if (bWasDrag)
	{
		for (APlayerUnit* Unit : DragHoveredUnits)
		{
			Unit->SetHovered(false);
		}
		
		TArray<APlayerUnit*> InRect;
		AEmberfallHUD* EmberfallHUD = Cast<AEmberfallHUD>(GetHUD());
		if (EmberfallHUD != nullptr)
		{
			GetUnitsInRect(DragStart, FVector2D{ MouseX, MouseY }, InRect);
		}
		
		DragHoveredUnits.Reset();
		ClearSelection();

		for (APlayerUnit* Unit : InRect)
		{
			Unit->SetSelected(true);
			SelectedUnits.Add(Unit);
		}
		return;
	}
	
	ClearSelection();
	
	if (HoveredUnit != nullptr)
	{
		HoveredUnit->SetSelected(true);
		SelectedUnits.Add(HoveredUnit);
	}
}

void AEmberfallPlayerController::ClearSelection()
{
	for (APlayerUnit* Unit : SelectedUnits)
	{
		Unit->SetSelected(false);
	}
	SelectedUnits.Reset();
}

void AEmberfallPlayerController::GetUnitsInRect(const FVector2D& A, const FVector2D& B, TArray<APlayerUnit*>& OutUnits)
{
	OutUnits.Reset();

	const FVector2D Min{ FMath::Min(A.X, B.X), FMath::Min(A.Y, B.Y) };
	const FVector2D Max{ FMath::Max(A.X, B.X), FMath::Max(A.Y, B.Y) };

	for (TActorIterator<APlayerUnit> It(GetWorld()); It; ++It)
	{
		APlayerUnit* Unit = *It;

		FVector2D ScreenPos;
		if (!ProjectWorldLocationToScreen(Unit->GetActorLocation(), ScreenPos))
		{
			continue;
		}

		if (ScreenPos.X >= Min.X && ScreenPos.X <= Max.X &&
			ScreenPos.Y >= Min.Y && ScreenPos.Y <= Max.Y)
		{
			OutUnits.Add(Unit);
		}
	}
}

void AEmberfallPlayerController::UpdateEdgeScroll(const FVector2D& MousePos) const
{
	ACameraPawn* CameraPawn = Cast<ACameraPawn>(GetPawn());
	if (CameraPawn == nullptr)
	{
		return;
	}

	int32 SizeX = 0;
	int32 SizeY = 0;
	GetViewportSize(SizeX, SizeY);

	// Screen Y grows downwards, so the top edge means "forward"
	FVector2D Input = FVector2D::ZeroVector;

	if (MousePos.X <= EdgeScrollMargin)
	{
		Input.X = -1.0f;
	}
	else if (MousePos.X >= SizeX - EdgeScrollMargin)
	{
		Input.X = 1.0f;
	}

	if (MousePos.Y <= EdgeScrollMargin)
	{
		Input.Y = 1.0f;
	}
	else if (MousePos.Y >= SizeY - EdgeScrollMargin)
	{
		Input.Y = -1.0f;
	}

	if (!Input.IsZero())
	{
		CameraPawn->AddPanInput(Input);
	}
}
