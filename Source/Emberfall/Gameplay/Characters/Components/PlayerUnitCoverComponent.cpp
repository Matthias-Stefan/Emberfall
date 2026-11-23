// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/Characters/Components/PlayerUnitCoverComponent.h"

#include "Emberfall/Gameplay/World/Cover/CoverLog.h"
#include "Emberfall/Gameplay/World/Cover/CoverSettings.h"
#include "Emberfall/Gameplay/World/Cover/CoverSubsystem.h"


UPlayerUnitCoverComponent::UPlayerUnitCoverComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.bStartWithTickEnabled = false;
}

void UPlayerUnitCoverComponent::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    
    switch (CoverState)
    {
        case ECoverState::Entering:
            TickEntering(DeltaTime);
            break;
        default:
            SetComponentTickEnabled(false);
            break;
    }
}

bool UPlayerUnitCoverComponent::TryEnterCover()
{
    if (CoverState == ECoverState::InCover || CoverState == ECoverState::Entering)
    {
        return true;
    }
    
    const AActor* Unit = GetOwner();
    if (!Unit)
    {
        UE_LOG(LogCover, Error, TEXT("TryEnterCover failed: %s has no owner."), *GetNameSafe(this));
        return false;
    }

    // GetCoverSubsystem logs the reason itself.
    const UCoverSubsystem* CoverSubsystem = GetCoverSubsystem();
    if (!CoverSubsystem)
    {
        return false;
    }

    const UCoverSettings& Settings = CoverSubsystem->GetSettings();

    TArray<FCoverEdgeHit> EdgeHits;
    CoverSubsystem->QueryCoverEdgesInDistance(Unit->GetActorLocation(), Settings.EntrySearchRadius, EdgeHits);
    if (EdgeHits.IsEmpty())
    {
        UE_LOG(LogCover, Verbose, TEXT("TryEnterCover: no cover edge within %.0f cm of %s."),
            Settings.EntrySearchRadius, *GetNameSafe(Unit));
        return false;
    }

    const FVector2D FacingDirection = FVector2D(Unit->GetActorForwardVector()).GetSafeNormal();

    const FCoverEdgeHit* BestHit = nullptr;
    double BestScore = TNumericLimits<double>::Max();
    for (const FCoverEdgeHit& EdgeHit : EdgeHits)
    {
        // 0 if the unit already faces away from the wall, 1 if it has to turn the full 180 degrees.
        const double AngleScore = (1.0 - FVector2D::DotProduct(FacingDirection, EdgeHit.OutwardNormal)) * 0.5;
        const double Score = Settings.EntryDistanceWeight * (EdgeHit.Distance / Settings.EntrySearchRadius)
                           + Settings.EntryAngleWeight * AngleScore;
        if (Score < BestScore)
        {
            BestScore = Score;
            BestHit = &EdgeHit;
        }
    }
    
    // BestHit stays null only if no score was comparable, which must not happen with a non-empty hit list.
    if (!BestHit)
    {
        UE_LOG(LogCover, Error, TEXT("TryEnterCover failed: %s found no best edge among %d hits."),
            *GetNameSafe(this), EdgeHits.Num());
        return false;
    }

    TargetEdgeHit = *BestHit;
    CoverState = ECoverState::Entering;
    SetComponentTickEnabled(true);
    
    return true;
}

void UPlayerUnitCoverComponent::LeaveCover()
{
    CoverState = ECoverState::None;
    SetComponentTickEnabled(false);
}

void UPlayerUnitCoverComponent::TickEntering(float DeltaTime)
{
    AActor* Unit = GetOwner();
    const UCoverSubsystem* CoverSubsystem = GetCoverSubsystem();
    if (!Unit || !CoverSubsystem)
    {
        UE_LOG(LogCover, Error, TEXT("TickEntering failed: %s has no owner or subsystem."), *GetNameSafe(this));
        LeaveCover();
        return;
    }
    
    const UCoverSettings& Settings = CoverSubsystem->GetSettings();

    const FVector UnitLocation = Unit->GetActorLocation();
    const FVector2D TargetPoint = TargetEdgeHit.ClosestPoint + TargetEdgeHit.OutwardNormal * Settings.EnterStandOffset;
    const FVector TargetLocation(TargetPoint.X, TargetPoint.Y, UnitLocation.Z);
    
    const FVector NewLocation = FMath::VInterpConstantTo(UnitLocation, TargetLocation, DeltaTime, Settings.EnterVelocity);
    Unit->SetActorLocation(NewLocation);
    
    if (NewLocation.Equals(TargetLocation, Settings.EnterArrivalTolerance))
    {
        CoverState = ECoverState::InCover;
        SetComponentTickEnabled(false);
    }
}

const UCoverSubsystem* UPlayerUnitCoverComponent::GetCoverSubsystem() const
{
    const UWorld* World = GetWorld();
    if (!World)
    {
        UE_LOG(LogCover, Error, TEXT("%s has no world."), *GetNameSafe(this));
        return nullptr;
    }

    const UCoverSubsystem* CoverSubsystem = World->GetSubsystem<UCoverSubsystem>();
    if (!CoverSubsystem)
    {
        UE_LOG(LogCover, Error, TEXT("%s found no UCoverSubsystem in the world."), *GetNameSafe(this));
        return nullptr;
    }

    return CoverSubsystem;
}