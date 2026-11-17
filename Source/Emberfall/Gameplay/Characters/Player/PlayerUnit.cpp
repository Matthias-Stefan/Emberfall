// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/Characters/Player/PlayerUnit.h"
#include "Emberfall/Core/EmberfallLog.h"
#include "Emberfall/Gameplay/Characters/Components/PlayerUnitCoverComponent.h"
#include "Emberfall/Gameplay/Characters/Components/PlayerUnitSelectionComponent.h"
#include "Emberfall/Gameplay/Characters/Player/PlayerUnitAIController.h"

#include "Components/CapsuleComponent.h"


APlayerUnit::APlayerUnit()
{
    PrimaryActorTick.bCanEverTick = false;

    GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);

    SelectionComponent = CreateDefaultSubobject<UPlayerUnitSelectionComponent>(TEXT("SelectionComponent"));
    CoverComponent = CreateDefaultSubobject<UPlayerUnitCoverComponent>(TEXT("CoverComponent"));
}

void APlayerUnit::MoveToTarget(const FVector& Target)
{
    APlayerUnitAIController* AIController = Cast<APlayerUnitAIController>(GetController());
    if (AIController == nullptr)
    {
        UE_LOG(LogEmberfall, Warning, TEXT("%s has no APlayerUnitAIController"), *GetNameSafe(this));
        return;
    }

    AIController->MoveToLocation(Target, -1.f, true, true, true);
}