// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/Characters/Components/PlayerUnitCoverComponent.h"

#include "Emberfall/Gameplay/World/Cover/CoverLog.h"
#include "Emberfall/Gameplay/World/Cover/CoverSettings.h"
#include "Emberfall/Gameplay/World/Cover/CoverSubsystem.h"


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

    const UWorld* World = GetWorld();
    if (!World)
    {
        UE_LOG(LogCover, Error, TEXT("TryEnterCover failed: %s has no world."), *GetNameSafe(this));
        return false;
    }
    
    const UCoverSubsystem* CoverSubsystem = World->GetSubsystem<UCoverSubsystem>();
    if (!CoverSubsystem)
    {
        UE_LOG(LogCover, Error, TEXT("TryEnterCover failed: %s found no UCoverSubsystem in the world."), *GetNameSafe(this));
        return false;
    }
    
    const AActor* Unit = GetOwner();
    if (!Unit)
    {
        UE_LOG(LogCover, Error, TEXT("TryEnterCover failed: %s has no owner."), *GetNameSafe(this));
        return false;
    }
    
    constexpr float Radius = 120.0f;
    
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
    
    int x = 5;
    // Next step: dock the unit at BestHit->ClosestPoint and set bIsInCover.
    
    return false;
}

void UPlayerUnitCoverComponent::LeaveCover()
{
    bIsInCover = false;
}