// Copyright (c) 2026 Emberfall. All Rights Reserved.


#include "Emberfall/Gameplay/Characters/Components/Cover/CoverComponent.h"
#include "Emberfall/Core/EmberfallLog.h"
#include "Emberfall/Gameplay/World/CoverObject.h"

#include "Components/SplineComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"


UCoverComponent::UCoverComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.bStartWithTickEnabled = false;
}

void UCoverComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (IsDocking())
    {
        DockData.Alpha = FMath::Min(DockData.Alpha + DeltaTime / FMath::Max(DockDuration, UE_KINDA_SMALL_NUMBER), 1.0f);
        const float Eased = FMath::InterpEaseInOut(0.0f, 1.0f, DockData.Alpha, 2.0f);

        AActor* Actor = GetOwner();
        if (Actor == nullptr)
        {
            UE_LOG(LogEmberfall, Error, TEXT("%s: No owner, dock slide aborted."), *GetNameSafe(this));
            CoverState = ECoverState::None;
            SetComponentTickEnabled(false);
            return;
        }
        Actor->SetActorLocation(FMath::Lerp(DockData.StartLocation, DockData.TargetLocation, Eased));
        Actor->SetActorRotation(FQuat::Slerp(DockData.StartRotation, DockData.TargetRotation, Eased));

        if (const ACharacter* OwnerCharacter = Cast<ACharacter>(Actor))
        {
            const FVector Shift = FVector::ForwardVector * CoverMeshOffset * Eased;
            OwnerCharacter->GetMesh()->SetRelativeLocation(DockData.MeshStartLocation + Shift);
        }
        
        if (DockData.Alpha >= 1.0f)
        {
            CoverState = ECoverState::InCover;
            SetComponentTickEnabled(false);
        }
    }
}

FVector UCoverComponent::ConstrainToCover(const FVector& Target) const
{
    switch (CoverState)
    {
        case ECoverState::Docking:
        {
            // Unit is sliding, it must not move on its own
            const AActor* OwnerActor = GetOwner();
            return OwnerActor != nullptr ? OwnerActor->GetActorLocation() : Target;
        }

        case ECoverState::InCover:
        {
            if (!Spline.IsValid())
            {
                return Target;
            }

            FVector OnLine = Spline->FindLocationClosestToWorldLocation(Target, ESplineCoordinateSpace::World);
            OnLine.Z = Target.Z;
            return OnLine;
        }

        case ECoverState::None:
        default:
        {
            return Target;
        }
    }
}

bool UCoverComponent::TryEnterCover()
{
    if (CoverState != ECoverState::None)
    {
        return false;
    }

    const ACharacter* OwnerCharacter = Cast<ACharacter>(GetOwner());
    if (OwnerCharacter == nullptr)
    {
        UE_LOG(LogEmberfall, Error, TEXT("%s: Owner is not an ACharacter."), *GetNameSafe(this));
        return false;
    }
    
    //
    // Trace
    //

    const FVector Start = OwnerCharacter->GetActorLocation();
    const FVector End = Start + OwnerCharacter->GetActorForwardVector() * CoverTraceDistance;

    FHitResult Hit{};
    const FCollisionQueryParams TraceParams(SCENE_QUERY_STAT(CoverTrace), false, OwnerCharacter);
    if (!GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_COVER, TraceParams))
    {
        return false;
    }

    const ACoverObject* Cover = Cast<ACoverObject>(Hit.GetActor());
    if (Cover == nullptr || !Cover->CanDockFromNormal(Hit.ImpactNormal))
    {
        return false;
    }

    USplineComponent* CoverLine = Cover->GetCoverLine();
    if (CoverLine == nullptr)
    {
        return false;
    }
    
    //
    // Dock target
    //

    Spline = CoverLine;
    CoverNormal = Cover->GetDockNormal().GetSafeNormal2D();

    FVector Target = CoverLine->FindLocationClosestToWorldLocation(Start, ESplineCoordinateSpace::World);
    Target.Z = Start.Z;

    DockData.StartLocation = Start;
    DockData.TargetLocation = Target;
    DockData.StartRotation = OwnerCharacter->GetActorQuat();
    DockData.TargetRotation = FRotator(0.f, (-CoverNormal).Rotation().Yaw, 0.f).Quaternion();
    DockData.Alpha = 0.f;
    DockData.MeshStartLocation = OwnerCharacter->GetMesh()->GetRelativeLocation();
    
    //
    // Start docking
    //

    if (AController* OwnController = OwnerCharacter->GetController())
    {
        OwnController->StopMovement();
    }

    OwnerCharacter->GetCharacterMovement()->bOrientRotationToMovement = false;

    CoverState = ECoverState::Docking;
    SetComponentTickEnabled(true);
    return true;
}

void UCoverComponent::LeaveCover()
{
    if (CoverState == ECoverState::None)
    {
        return;
    }

    // Also covers leaving in the middle of the dock slide
    SetComponentTickEnabled(false);

    if (const ACharacter* OwnerCharacter = Cast<ACharacter>(GetOwner()))
    {
        OwnerCharacter->GetCharacterMovement()->bOrientRotationToMovement = true;
        OwnerCharacter->GetMesh()->SetRelativeLocation(DockData.MeshStartLocation);
    }

    Spline.Reset();
    CoverNormal = FVector::ZeroVector;
    DockData = FCoverDockData{};
    CoverState = ECoverState::None;
}
