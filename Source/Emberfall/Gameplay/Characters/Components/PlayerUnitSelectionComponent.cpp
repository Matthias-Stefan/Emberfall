// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/Characters/Components/PlayerUnitSelectionComponent.h"


UPlayerUnitSelectionComponent::UPlayerUnitSelectionComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UPlayerUnitSelectionComponent::SetHovered(const bool bInHovered)
{
    if (bHovered == bInHovered)
    {
        return;
    }

    bHovered = bInHovered;
    UpdateSelectionState();
}

void UPlayerUnitSelectionComponent::SetSelected(const bool bInSelected)
{
    if (bSelected == bInSelected)
    {
        return;
    }

    bSelected = bInSelected;
    UpdateSelectionState();
}

void UPlayerUnitSelectionComponent::UpdateSelectionState()
{
    EPlayerUnitTypes NewState = EPlayerUnitTypes::None;
    if (bSelected)
    {
        NewState = EPlayerUnitTypes::Selected;
    }
    else if (bHovered)
    {
        NewState = EPlayerUnitTypes::Hovered;
    }

    if (NewState == SelectionState)
    {
        return;
    }

    SelectionState = NewState;
    OnSelectionStateChanged.Broadcast(SelectionState);
}