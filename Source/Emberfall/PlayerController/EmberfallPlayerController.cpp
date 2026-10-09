// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/PlayerController/EmberfallPlayerController.h"
#include "Emberfall/Camera/CameraPawn.h"
#include "Emberfall/Core/EmberfallLog.h"
#include "Emberfall/Gameplay/Characters/Player/PlayerUnit.h"
#include "Emberfall/Gameplay/Characters/Player/PlayerUnitAIController.h"
#include "Emberfall/PlayerController/Selection/SelectionComponent.h"

#include "EngineUtils.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"


AEmberfallPlayerController::AEmberfallPlayerController()
{
	PrimaryActorTick.bCanEverTick = true;

	bShowMouseCursor = true;
	DefaultMouseCursor = EMouseCursor::Default;

	SelectionComponent = CreateDefaultSubobject<USelectionComponent>(TEXT("SelectionComponent"));
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

	// Each action is checked on its own, so all missing assets show up in one run
	if (SelectAction != nullptr)
	{
		EnhancedInput->BindAction(SelectAction, ETriggerEvent::Started, this, &AEmberfallPlayerController::OnSelectStarted);
		EnhancedInput->BindAction(SelectAction, ETriggerEvent::Completed, this, &AEmberfallPlayerController::OnSelectCompleted);
	}
	else
	{
		UE_LOG(LogEmberfall, Error, TEXT("%s: SelectAction is not set."), *GetNameSafe(this));
	}

	if (AddToSelectionAction != nullptr)
	{
		EnhancedInput->BindAction(AddToSelectionAction, ETriggerEvent::Started, this, &AEmberfallPlayerController::OnAddToSelectionStarted);
		EnhancedInput->BindAction(AddToSelectionAction, ETriggerEvent::Completed, this, &AEmberfallPlayerController::OnAddToSelectionCompleted);
	}
	else
	{
		UE_LOG(LogEmberfall, Error, TEXT("%s: AddToSelectionAction is not set."), *GetNameSafe(this));
	}

	if (CommandAction != nullptr)
	{
		EnhancedInput->BindAction(CommandAction, ETriggerEvent::Started, this, &AEmberfallPlayerController::OnCommandStarted);
	}
	else
	{
		UE_LOG(LogEmberfall, Error, TEXT("%s: CommandAction is not set."), *GetNameSafe(this));
	}
}


void AEmberfallPlayerController::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	// TEMP: remove with IA_ToggleCover / IA_LeaveCover
	{
		if (WasInputKeyJustPressed(EKeys::C))
		{
			for (TActorIterator<APlayerUnit> It(GetWorld()); It; ++It)
			{
				It->TryEnterCover();
			}
		}

		if (WasInputKeyJustPressed(EKeys::V))
		{
			for (TActorIterator<APlayerUnit> It(GetWorld()); It; ++It)
			{
				It->SetInCover(false);
			}
		}	
	}
	
	//
	// Hover
	//

	SelectionComponent->UpdateHover();

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

	SelectionComponent->UpdateDrag(MousePos);

	//
	// Edge scrolling
	//

	if (bEdgeScrollEnabled)
	{
		UpdateEdgeScroll(MousePos);
	}
}

void AEmberfallPlayerController::OnSelectStarted([[maybe_unused]] const FInputActionValue& Value)
{
	float MouseX{ 0.0f };
	float MouseY{ 0.0f };
	if (!GetMousePosition(MouseX, MouseY))
	{
		UE_LOG(LogEmberfall, Verbose, TEXT("%s: No mouse position, drag not started."), *GetNameSafe(this));
		return;
	}

	SelectionComponent->BeginPress(FVector2D{ MouseX, MouseY });
}

void AEmberfallPlayerController::OnSelectCompleted([[maybe_unused]] const FInputActionValue& Value)
{
	float MouseX = 0.0f;
	float MouseY = 0.0f;
	if (!GetMousePosition(MouseX, MouseY))
	{
		// Release outside the viewport: drop the press, otherwise it would stay stuck
		UE_LOG(LogEmberfall, Verbose, TEXT("%s: No mouse position, press cancelled."), *GetNameSafe(this));
		SelectionComponent->CancelPress();
		return;
	}

	SelectionComponent->EndPress(FVector2D{ MouseX, MouseY });
}

void AEmberfallPlayerController::OnAddToSelectionStarted([[maybe_unused]] const FInputActionValue& Value)
{
	SelectionComponent->SetAddMode(true);
}

void AEmberfallPlayerController::OnAddToSelectionCompleted([[maybe_unused]] const FInputActionValue& Value)
{
	SelectionComponent->SetAddMode(false);
}

void AEmberfallPlayerController::OnCommandStarted([[maybe_unused]] const FInputActionValue& Value)
{
	const TArray<TObjectPtr<APlayerUnit>> SelectedUnits = SelectionComponent->GetSelectedUnits();
	if (SelectedUnits.IsEmpty())
	{
		return;
	}
	
	FHitResult Hit;
	if (!GetHitResultUnderCursor(ECC_Visibility, false, Hit))
	{
		return;
	}
	
	for (auto& Unit : SelectedUnits)
	{
		if (!IsValid(Unit))
		{
			continue;
		}
		
		APlayerUnitAIController* UnitController = Cast<APlayerUnitAIController>(Unit->GetController());
		if (UnitController == nullptr)
		{
			UE_LOG(LogTemp, Warning, TEXT("%s has no APlayerUnitAIController"), *GetNameSafe(Unit));
			continue;
		}

		UnitController->MoveToLocation(Hit.Location, -1.f, true, true, true);
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