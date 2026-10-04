// Copyright (c) 2026 Emberfall. All Rights Reserved.


#include "CameraPawn.h"

#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"


ACameraPawn::ACameraPawn()
{
	PrimaryActorTick.bCanEverTick = false;
	
	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);
	
	SpringArm = CreateDefaultSubobject<USpringArmComponent>(TEXT("SpringArm"));
	SpringArm->SetupAttachment(Root);
	SpringArm->TargetArmLength = ArmLength;
	SpringArm->SetRelativeRotation(FRotator(Pitch, 0.0f, 0.0f));
	SpringArm->bDoCollisionTest = false;
	
	Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
	Camera->SetupAttachment(SpringArm, USpringArmComponent::SocketName);
}

void ACameraPawn::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	UEnhancedInputComponent* EnhancedInputComponent = Cast<UEnhancedInputComponent>(PlayerInputComponent);
	if (EnhancedInputComponent == nullptr)
	{
		UE_LOG(LogTemp, Warning, TEXT("%s: input component is not a UEnhancedInputComponent"), *GetNameSafe(this));
		return;
	}

	if (PanAction == nullptr)
	{
		UE_LOG(LogTemp, Warning, TEXT("%s: PanAction is not assigned"), *GetNameSafe(this));
		return;
	}

	if (ZoomAction == nullptr)
	{
		UE_LOG(LogTemp, Warning, TEXT("%s: ZoomAction is not assigned"), *GetNameSafe(this));
		return;
	}
	
	if (RotateModeAction == nullptr)
	{
		UE_LOG(LogTemp, Warning, TEXT("%s: RotateModeAction is not assigned"), *GetNameSafe(this));
		return;
	}

	if (LookAction == nullptr)
	{
		UE_LOG(LogTemp, Warning, TEXT("%s: LookAction is not assigned"), *GetNameSafe(this));
		return;
	}

	EnhancedInputComponent->BindAction(PanAction, ETriggerEvent::Triggered, this, &ACameraPawn::Pan);
	EnhancedInputComponent->BindAction(ZoomAction, ETriggerEvent::Triggered, this, &ACameraPawn::Zoom);
	EnhancedInputComponent->BindAction(RotateModeAction, ETriggerEvent::Started, this, &ACameraPawn::OnRotateModeStarted);
	EnhancedInputComponent->BindAction(RotateModeAction, ETriggerEvent::Completed, this, &ACameraPawn::OnRotateModeCompleted);
	EnhancedInputComponent->BindAction(LookAction, ETriggerEvent::Triggered, this, &ACameraPawn::Look);
}

void ACameraPawn::BeginPlay()
{
	Super::BeginPlay();

	ArmLength = FMath::Clamp(ArmLength, MinArmLength, MaxArmLength);
	SpringArm->TargetArmLength = ArmLength;
	SpringArm->SetRelativeRotation(FRotator(Pitch, 0.0f, 0.0f));
	SetActorRotation(FRotator(0.0f, Yaw, 0.0f));
}

void ACameraPawn::PawnClientRestart()
{
	Super::PawnClientRestart();

	const APlayerController* PlayerController = Cast<APlayerController>(GetController());
	if (PlayerController == nullptr)
	{
		// No controller yet is normal, not an error
		return;
	}

	const ULocalPlayer* LocalPlayer = PlayerController->GetLocalPlayer();
	UEnhancedInputLocalPlayerSubsystem* Subsystem =
		ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(LocalPlayer);
	if (Subsystem == nullptr)
	{
		UE_LOG(LogTemp, Warning, TEXT("%s: no EnhancedInput subsystem"), *GetNameSafe(this));
		return;
	}

	if (MappingContext == nullptr)
	{
		UE_LOG(LogTemp, Warning, TEXT("%s: MappingContext is not assigned"), *GetNameSafe(this));
		return;
	}

	Subsystem->AddMappingContext(MappingContext, 0);
}

void ACameraPawn::Pan(const FInputActionValue& Value)
{
    const FVector2D Input = Value.Get<FVector2D>();
    const float DeltaSeconds = GetWorld()->GetDeltaSeconds();

	const FRotator YawRotation(0.0f, Yaw, 0.0f);
    const FVector Offset = YawRotation.RotateVector(FVector(Input.Y, Input.X, 0.0f));

    AddActorWorldOffset(Offset * PanSpeed * DeltaSeconds);
}

void ACameraPawn::Zoom(const FInputActionValue& Value)
{
	const float Axis = Value.Get<float>();

	ArmLength = FMath::Clamp(ArmLength - Axis * ZoomStep, MinArmLength, MaxArmLength);
	SpringArm->TargetArmLength = ArmLength;
}

void ACameraPawn::OnRotateModeStarted()
{
	bRotating = true;
}

void ACameraPawn::OnRotateModeCompleted()
{
	bRotating = false;
}

void ACameraPawn::Look(const FInputActionValue& Value)
{
	if (!bRotating)
	{
		return;
	}

	Yaw = FRotator::NormalizeAxis(Yaw + Value.Get<float>() * RotateSensitivity);
	SetActorRotation(FRotator(0.0f, Yaw, 0.0f));
}
