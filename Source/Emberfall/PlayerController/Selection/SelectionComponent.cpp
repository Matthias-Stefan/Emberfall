// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/PlayerController/Selection/SelectionComponent.h"
#include "Emberfall/Characters/Player/PlayerUnit.h"
#include "Emberfall/EmberfallLog.h"

#include "EngineUtils.h"


USelectionComponent::USelectionComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void USelectionComponent::UpdateHover()
{
	if (OwnerController == nullptr || DragState.IsDragging())
	{
		return;
	}

	FHitResult Hit = {};
	OwnerController->GetHitResultUnderCursor(ECC_Visibility, false, Hit);
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

void USelectionComponent::UpdateDrag(const FVector2D& MousePos)
{
	DragState.Update(MousePos, DragThreshold);
	if (!DragState.IsDragging())
	{
		return;
	}

	TArray<APlayerUnit*> InRect;
	GetUnitsInRect(DragState.GetDragStart(), MousePos, InRect);

	//
	// Un-hover units that left the box
	//

	for (APlayerUnit* Unit : DragHoveredUnits)
	{
		if (Unit != nullptr && !InRect.Contains(Unit))
		{
			Unit->SetHovered(false);
		}
	}

	//
	// Hover units inside the box
	//

	DragHoveredUnits.Reset();
	for (APlayerUnit* Unit : InRect)
	{
		Unit->SetHovered(true);
		DragHoveredUnits.Add(Unit);
	}
}

void USelectionComponent::BeginPress(const FVector2D& MousePos)
{
	DragState.Begin(MousePos);
}

void USelectionComponent::EndPress(const FVector2D& MousePos)
{
	const FVector2D DragStart = DragState.GetDragStart();
	const bool bWasDrag = DragState.Complete();

	//
	// Box selection
	//

	if (bWasDrag)
	{
		// Drag hover is over, the selection state stays untouched
		for (APlayerUnit* Unit : DragHoveredUnits)
		{
			if (Unit != nullptr)
			{
				Unit->SetHovered(false);
			}
		}
		DragHoveredUnits.Reset();

		TArray<APlayerUnit*> InRect;
		GetUnitsInRect(DragStart, MousePos, InRect);

		if (!bAddToSelection)
		{
			ClearSelection();
		}

		for (APlayerUnit* Unit : InRect)
		{
			Unit->SetSelected(true);
			SelectedUnits.AddUnique(Unit);
		}
		return;
	}

	//
	// Click selection
	//

	if (!bAddToSelection)
	{
		ClearSelection();
	}

	if (HoveredUnit == nullptr)
	{
		return;
	}

	if (bAddToSelection && SelectedUnits.Contains(HoveredUnit))
	{
		// Shift-click on a selected unit toggles it off
		HoveredUnit->SetSelected(false);
		SelectedUnits.Remove(HoveredUnit);
	}
	else
	{
		HoveredUnit->SetSelected(true);
		SelectedUnits.AddUnique(HoveredUnit);
	}
}

void USelectionComponent::CancelPress()
{
	DragState.Reset();

	for (APlayerUnit* Unit : DragHoveredUnits)
	{
		if (Unit != nullptr)
		{
			Unit->SetHovered(false);
		}
	}
	DragHoveredUnits.Reset();
}

void USelectionComponent::BeginPlay()
{
	Super::BeginPlay();

	OwnerController = Cast<APlayerController>(GetOwner());
	if (OwnerController == nullptr)
	{
		UE_LOG(LogEmberfall, Error, TEXT("%s: Owner is not a PlayerController."), *GetNameSafe(this));
	}
}

void USelectionComponent::ClearSelection()
{
	for (APlayerUnit* Unit : SelectedUnits)
	{
		if (Unit != nullptr)
		{
			Unit->SetSelected(false);
		}
	}
	SelectedUnits.Reset();
}

void USelectionComponent::GetUnitsInRect(const FVector2D& A, const FVector2D& B, TArray<APlayerUnit*>& OutUnits) const
{
	OutUnits.Reset();

	if (OwnerController == nullptr)
	{
		return;
	}

	const FVector2D Min{ FMath::Min(A.X, B.X), FMath::Min(A.Y, B.Y) };
	const FVector2D Max{ FMath::Max(A.X, B.X), FMath::Max(A.Y, B.Y) };

	for (TActorIterator<APlayerUnit> It(GetWorld()); It; ++It)
	{
		APlayerUnit* Unit = *It;

		FVector2D ScreenPos;
		if (!OwnerController->ProjectWorldLocationToScreen(Unit->GetActorLocation(), ScreenPos))
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