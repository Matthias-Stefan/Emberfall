// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/Characters/Player/PlayerUnit.h"
#include "Emberfall/Core/EmberfallLog.h"
#include "Emberfall/Gameplay/Characters/Components/Cover/CoverComponent.h"
#include "Emberfall/Gameplay/Characters/Player/PlayerUnitAIController.h"
#include "Emberfall/Gameplay/Characters/Player/PlayerUnitTypes.h"

#include "Components/CapsuleComponent.h"


APlayerUnit::APlayerUnit()
{
    PrimaryActorTick.bCanEverTick = false;

    CoverComponent = CreateDefaultSubobject<UCoverComponent>(TEXT("CoverComponent"));
    GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
}

void APlayerUnit::MoveToTarget(const FVector& Target)
{
    APlayerUnitAIController* AIController = Cast<APlayerUnitAIController>(GetController());
    if (AIController == nullptr)
    {
        UE_LOG(LogEmberfall, Warning, TEXT("%s has no APlayerUnitAIController"), *GetNameSafe(this));
        return;
    }

    const ECoverState State = CoverComponent->GetCoverState();

    if (State == ECoverState::Docking)
    {
        return;
    }

    const bool bUseNavmesh = (State == ECoverState::None);
    const FVector Destination = CoverComponent->ConstrainToCover(Target);

    AIController->MoveToLocation(Destination, -1.f, true, bUseNavmesh, bUseNavmesh);
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
        bSelected ? EPlayerUnitTypes::Selected : bHovered ? EPlayerUnitTypes::Hovered : EPlayerUnitTypes::None;

    if (NewSelectionState == SelectionState)
    {
        return;
    }

    SelectionState = NewSelectionState;
    OnSelectionStateChanged(SelectionState);
}
