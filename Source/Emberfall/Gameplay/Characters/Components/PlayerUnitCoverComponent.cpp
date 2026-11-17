// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/Characters/Components/PlayerUnitCoverComponent.h"


UPlayerUnitCoverComponent::UPlayerUnitCoverComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UPlayerUnitCoverComponent::TryEnterCover()
{
    if (bIsInCover)
    {
        return true;
    }

    // Next step: ask UCoverSubsystem for the nearest ACoverObject and dock to it
    return false;
}

void UPlayerUnitCoverComponent::LeaveCover()
{
    bIsInCover = false;
}