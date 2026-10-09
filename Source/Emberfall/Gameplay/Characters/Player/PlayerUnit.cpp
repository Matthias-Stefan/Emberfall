// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/Characters/Player/PlayerUnit.h"
#include "Emberfall/Gameplay/Characters/Player/PlayerUnitTypes.h"

#include "Components/CapsuleComponent.h"
#include "Components/SplineComponent.h"
#include "Emberfall/Gameplay/World/CoverObject.h"


APlayerUnit::APlayerUnit()
{
	PrimaryActorTick.bCanEverTick = false;
	
	GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
}

void APlayerUnit::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	
	if (bIsDocking)
	{
		DockAlpha = FMath::Min(DockAlpha + DeltaTime / FMath::Max(DockDuration, UE_KINDA_SMALL_NUMBER), 1.f);
		const float Eased = FMath::InterpEaseInOut(0.f, 1.f, DockAlpha, 2.f);

		SetActorLocation(FMath::Lerp(DockStartLocation, DockTargetLocation, Eased));
		SetActorRotation(FQuat::Slerp(DockStartRotation, DockTargetRotation, Eased));

		if (DockAlpha >= 1.0f)
		{
			bIsDocking = false;
		}
	}
}

void APlayerUnit::SetHovered(bool bInHovered)
{
	if (bHovered == bInHovered)
	{
		return;
	}

	bHovered = bInHovered;
	UpdateSelectionState();
}

void APlayerUnit::SetSelected(bool bInSelected)
{
	if (bSelected == bInSelected)
	{
		return;
	}

	bSelected = bInSelected;
	UpdateSelectionState();
}

FVector APlayerUnit::ConstrainToCover(const FVector& Target) const
{
	if (!bIsInCover || !CoverSpline.IsValid())
	{
		return Target;
	}

	if (bIsDocking)
	{
		return GetActorLocation();
	}

	FVector OnLine = CoverSpline->FindLocationClosestToWorldLocation(Target, ESplineCoordinateSpace::World);
	OnLine.Z = Target.Z;
	return OnLine;
}

bool APlayerUnit::TryEnterCover()
{
	const FVector Start = GetActorLocation();
	const FVector End = Start + GetActorForwardVector() * CoverTraceDistance;
	
	FHitResult Hit{};
	FCollisionQueryParams TraceParams(SCENE_QUERY_STAT(CoverTrace), false, this);
	if (!GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_COVER, TraceParams))
	{
		return false;
	}
	
	ACoverObject* Cover = Cast<ACoverObject>(Hit.GetActor());
	if (!Cover || !Cover->CanDockFromNormal(Hit.ImpactNormal))
	{
		return false;
	}
	
	CoverSpline = Cover->GetCoverLine();
	CoverNormal = Cover->GetDockNormal().GetSafeNormal2D();
	
	FVector Target = CoverSpline->FindLocationClosestToWorldLocation(GetActorLocation(), ESplineCoordinateSpace::World);
	Target.Z = GetActorLocation().Z;

	DockStartLocation = GetActorLocation();
	DockTargetLocation = Target;
	DockStartRotation = GetActorQuat();
	DockTargetRotation = FRotator(0.f, (-CoverNormal).Rotation().Yaw, 0.f).Quaternion();
	DockAlpha = 0.f;
	bIsDocking = true;

	if (AController* OwnController = GetController())
	{
		OwnController->StopMovement();
	}

	SetInCover(true);
	return true;
}

void APlayerUnit::SetInCover(bool bInCover)
{
	bIsInCover = bInCover;
	GetCharacterMovement()->bOrientRotationToMovement = !bInCover;

	if (!bInCover)
	{
		bIsDocking = false;
		bIsCoverMoving = false;
	}
}

void APlayerUnit::UpdateSelectionState()
{
	const EPlayerUnitTypes NewSelectionState = 
		bSelected ? EPlayerUnitTypes::Selected :
		bHovered  ? EPlayerUnitTypes::Hovered : EPlayerUnitTypes::None;
	
	if (NewSelectionState == SelectionState)
	{
		return;
	}
	
	SelectionState = NewSelectionState;
	OnSelectionStateChanged(SelectionState);
}

