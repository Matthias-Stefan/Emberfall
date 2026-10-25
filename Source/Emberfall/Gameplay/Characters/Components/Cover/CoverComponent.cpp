// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/Characters/Components/Cover/CoverComponent.h"
#include "Emberfall/Core/EmberfallLog.h"
#include "Emberfall/Gameplay/World/Cover/CoverObject.h"
#include "Emberfall/Gameplay/World/Cover/CoverPath.h"
#include "Emberfall/Gameplay/World/Cover/CoverSubsystem.h"

#include "Components/CapsuleComponent.h"
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
        }
    }
    else if (IsInCover())
    {
        const float Speed = GetSignedCoverSpeed();
        if (FMath::Abs(Speed) > MirrorSpeedThreshold)
        {
            bLastMoveRight = Speed > 0.0f;
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
            if (!CoverPath.IsValid())
            {
                return Target;
            }

            const float Distance = ClampToPathMargins(CoverPath->FindDistanceClosestTo(Target));
            FVector OnLine = CoverPath->GetLocationAtDistance(Distance);
            
            const AActor* OwnerActor = GetOwner();
            if (OwnerActor != nullptr)
            {
                OnLine.Z = OwnerActor->GetActorLocation().Z;
            }
            
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

    ACoverObject* Cover = Cast<ACoverObject>(Hit.GetActor());
    if (Cover == nullptr)
    {
        return false;
    }
    
    UCoverSubsystem* CoverSubsystem = GetWorld()->GetSubsystem<UCoverSubsystem>();
    if (CoverSubsystem == nullptr)
    {
        UE_LOG(LogEmberfall, Error, TEXT("%s: Unable to access the cover subsystem."), *GetNameSafe(this));
        return false;
    }
    
    // Invalid if the hit side is blocked, that is a normal miss and not an error
    const TWeakObjectPtr<UCoverPath> Path = CoverSubsystem->GetCoverPath(*Cover, Hit.ImpactNormal);
    if (!Path.IsValid())
    {
        return false;
    }
    CoverPath = Path;
    
    //
    // Dock target
    //
    
    const float DistanceOnPath = ClampToPathMargins(CoverPath->FindDistanceClosestTo(Start));
    CoverNormal = CoverPath->GetNormalAtDistance(DistanceOnPath).GetSafeNormal2D();

    FVector Target = CoverPath->GetLocationAtDistance(DistanceOnPath);
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
    CoverState = ECoverState::Docking;
    SetComponentTickEnabled(true);
    
    //
    // Movement
    //
    
    UCharacterMovementComponent* Movement = OwnerCharacter->GetCharacterMovement();
    Movement->bOrientRotationToMovement = false;
    DefaultMaxWalkSpeed = Movement->MaxWalkSpeed;
    Movement->MaxWalkSpeed = CoverMoveSpeed;

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
        UCharacterMovementComponent* Movement = OwnerCharacter->GetCharacterMovement();
        Movement->bOrientRotationToMovement = true;
        Movement->MaxWalkSpeed = DefaultMaxWalkSpeed;
        OwnerCharacter->GetMesh()->SetRelativeLocation(DockData.MeshStartLocation);
    }

    CoverPath.Reset();
    CoverNormal = FVector::ZeroVector;
    DockData = FCoverDockData{};
    bLastMoveRight = false;
    CoverState = ECoverState::None;
}

float UCoverComponent::GetSignedCoverSpeed() const
{
    if (!IsInCover())
    {
        return 0.0f;
    }

    const AActor* OwnerActor = GetOwner();
    if (OwnerActor == nullptr)
    {
        return 0.0f;
    }

    return FVector::DotProduct(OwnerActor->GetVelocity(), OwnerActor->GetActorRightVector());
}

float UCoverComponent::ClampToPathMargins(float Distance) const
{
    if (!CoverPath.IsValid())
    {
        return Distance;
    }
    
    float Margin = EndMargin;
    if (Margin < 0.0f)
    {
        const ACharacter* OwnerCharacter = Cast<ACharacter>(GetOwner());
        Margin = OwnerCharacter != nullptr ? OwnerCharacter->GetCapsuleComponent()->GetScaledCapsuleRadius() : 0.0f;
    }
    
    const float Length = CoverPath->GetLength();
    if (Length <= Margin * 2.0f)
    {
        return Length * 0.5f;
    }

    return FMath::Clamp(Distance, Margin, Length - Margin);
}
