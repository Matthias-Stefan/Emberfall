// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/Characters/Player/PlayerUnit.h"
#include "Emberfall/Gameplay/Characters/Player/PlayerUnitTypes.h"
#include "Emberfall/Gameplay/Characters/Components/Cover/CoverComponent.h"

#include "Components/CapsuleComponent.h"


APlayerUnit::APlayerUnit()
{
	PrimaryActorTick.bCanEverTick = false;
	
	CoverComponent = CreateDefaultSubobject<UCoverComponent>(TEXT("CoverComponent"));
	GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
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

