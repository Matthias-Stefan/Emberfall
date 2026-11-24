// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/Characters/Components/PlayerUnitCoverComponent.h"

#include "Emberfall/Gameplay/World/Cover/CoverLog.h"
#include "Emberfall/Gameplay/World/Cover/CoverSettings.h"
#include "Emberfall/Gameplay/World/Cover/CoverSubsystem.h"

#include "GameFramework/Controller.h"
#include "GameFramework/Pawn.h"


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
        case ECoverState::InCover:
            TickInCover(DeltaTime);
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

    // The unit walks on the outline loop of the wall's group, so entering and walking along the wall share one line.
    // The loop is chosen by the point it should have next to the picked edge, not by the unit position.
    const FVector2D ExpectedPathPoint = BestHit->ClosestPoint + BestHit->OutwardNormal * Settings.OutlineOffset;
    FPolyline2D Path = FPolyline2D::Invalid;
    if (!CoverSubsystem->FindCoverPath(BestHit->CoverObject.Get(), ExpectedPathPoint, Path))
    {
        UE_LOG(LogCover, Warning, TEXT("TryEnterCover: %s found no cover path for the edge of %s."),
            *GetNameSafe(Unit), *GetNameSafe(BestHit->CoverObject.Get()));
        return false;
    }

    CoverPath = MoveTemp(Path);
    CoverPathLength = CoverPath.GetLength();
    // Only the distance along the path is needed, the point itself is recomputed from it every tick.
    static_cast<void>(CoverPath.FindClosestPoint(FVector2D(Unit->GetActorLocation()), DistanceAlongPath));
    TargetDistanceAlongPath = DistanceAlongPath;

    // A running AI move would fight the cover movement.
    if (const APawn* Pawn = Cast<APawn>(Unit))
    {
        if (AController* Controller = Pawn->GetController())
        {
            Controller->StopMovement();
        }
    }

    CoverState = ECoverState::Entering;
    SetComponentTickEnabled(true);
    
    return true;
}

void UPlayerUnitCoverComponent::LeaveCover()
{
    CoverState = ECoverState::None;
    CoverPath = FPolyline2D::Invalid;
    CoverPathLength = 0.0;
    DistanceAlongPath = 0.0;
    TargetDistanceAlongPath = 0.0;
    SetComponentTickEnabled(false);
}

bool UPlayerUnitCoverComponent::MoveAlongCover(const FVector& WorldTarget)
{
    if (CoverState != ECoverState::InCover || !CoverPath.IsValid())
    {
        return false;
    }

    // Clicks beside the line land on the closest point of the path.
    static_cast<void>(CoverPath.FindClosestPoint(FVector2D(WorldTarget.X, WorldTarget.Y), TargetDistanceAlongPath));
    SetComponentTickEnabled(true);
    return true;
}

void UPlayerUnitCoverComponent::TickEntering(float DeltaTime)
{
    AActor* Unit = GetOwner();
    const UCoverSubsystem* CoverSubsystem = GetCoverSubsystem();
    if (!Unit || !CoverSubsystem || !CoverPath.IsValid())
    {
        UE_LOG(LogCover, Error, TEXT("TickEntering failed: %s has no owner, subsystem or path."), *GetNameSafe(this));
        LeaveCover();
        return;
    }
    
    const UCoverSettings& Settings = CoverSubsystem->GetSettings();

    const FVector UnitLocation = Unit->GetActorLocation();
    const FVector2D TargetPoint = CoverPath.GetPointAtDistance(DistanceAlongPath);
    const FVector TargetLocation(TargetPoint.X, TargetPoint.Y, UnitLocation.Z);
    
    const FVector NewLocation = FMath::VInterpConstantTo(UnitLocation, TargetLocation, DeltaTime, Settings.EnterVelocity);
    Unit->SetActorLocation(NewLocation);
    
    if (NewLocation.Equals(TargetLocation, Settings.EnterArrivalTolerance))
    {
        CoverState = ECoverState::InCover;
        SetComponentTickEnabled(false);
    }
}

void UPlayerUnitCoverComponent::TickInCover(float DeltaTime)
{
    AActor* Unit = GetOwner();
    const UCoverSubsystem* CoverSubsystem = GetCoverSubsystem();
    if (!Unit || !CoverSubsystem || !CoverPath.IsValid())
    {
        UE_LOG(LogCover, Error, TEXT("TickInCover failed: %s has no owner, subsystem or path."), *GetNameSafe(this));
        LeaveCover();
        return;
    }

    const UCoverSettings& Settings = CoverSubsystem->GetSettings();

    // Signed distance still to walk, positive runs toward the end of the path.
    double Remaining = TargetDistanceAlongPath - DistanceAlongPath;
    if (CoverPath.IsClosed() && CoverPathLength > 0.0)
    {
        // A closed path has two ways to the target, take the shorter one.
        Remaining = FMath::Fmod(Remaining, CoverPathLength);
        if (Remaining > CoverPathLength * 0.5)
        {
            Remaining -= CoverPathLength;
        }
        else if (Remaining < -CoverPathLength * 0.5)
        {
            Remaining += CoverPathLength;
        }
    }

    const double MaxStep = Settings.CoverMoveVelocity * DeltaTime;
    if (FMath::Abs(Remaining) <= MaxStep)
    {
        DistanceAlongPath = TargetDistanceAlongPath;
        SetComponentTickEnabled(false);
    }
    else
    {
        DistanceAlongPath += FMath::Sign(Remaining) * MaxStep;
    }

    if (CoverPath.IsClosed() && CoverPathLength > 0.0)
    {
        DistanceAlongPath = FMath::Fmod(DistanceAlongPath, CoverPathLength);
        if (DistanceAlongPath < 0.0)
        {
            DistanceAlongPath += CoverPathLength;
        }
    }

    const FVector2D PathPoint = CoverPath.GetPointAtDistance(DistanceAlongPath);
    Unit->SetActorLocation(FVector(PathPoint.X, PathPoint.Y, Unit->GetActorLocation().Z));
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