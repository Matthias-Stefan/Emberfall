// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Emberfall/Gameplay/World/Cover/CoverTypes.h"

#include "PlayerUnitCoverComponent.generated.h"


class UCoverSubsystem;
/**
 * @brief Manages the cover state of an @c APlayerUnit.
 */
UCLASS(ClassGroup = (Emberfall), meta = (BlueprintSpawnableComponent))
class EMBERFALL_API UPlayerUnitCoverComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPlayerUnitCoverComponent();

    /**
     * @brief Moves the unit to the target cover edge while it is entering cover.
     * @param DeltaTime is the time since the last tick in seconds.
     * @param TickType is the kind of tick this is.
     * @param ThisTickFunction is the tick function that triggered this call.
     */
    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;
    
    /**
     * @brief Tries to take cover at the nearest suitable cover object.
     * @return @c true if the unit entered cover, otherwise @c false.
     */
    bool TryEnterCover();

    /**
     * @brief Leaves the current cover and clears @c bIsInCover.
     */
    void LeaveCover();

    /**
     * @brief Tests whether the owning unit stands in cover.
     * @return @c true if @c CoverState is @c ECoverState::InCover, otherwise @c false.
     */
    UFUNCTION(BlueprintPure, Category = "Cover")
    bool IsInCover() const { return CoverState == ECoverState::InCover; }

    /**
     * @brief Tests whether the owning unit is walking to its cover edge.
     * @return @c true if @c CoverState is @c ECoverState::Entering, otherwise @c false.
     */
    UFUNCTION(BlueprintPure, Category = "Cover")
    bool IsEntering() const { return CoverState == ECoverState::Entering; }
    
    
private:
    /**
     * @brief Moves the unit toward the target cover edge and switches to @c ECoverState::InCover on arrival.
     * @param DeltaTime is the time since the last tick in seconds.
     */
    void TickEntering(float DeltaTime);
    
    /**
     * @brief Finds the cover subsystem of the world this component lives in.
     * @return The cover subsystem, @c nullptr if there is no world or no subsystem.
     */
    const UCoverSubsystem* GetCoverSubsystem() const;
    
protected:
    /** @brief Current phase of this unit in the cover entry, hold and leave cycle. */
    UPROPERTY(VisibleInstanceOnly, Category = "Cover")
    ECoverState CoverState = ECoverState::None;
    
private:
    /** @brief Edge the unit is walking to or standing at, valid while @c CoverState is @c Entering or @c InCover. */
    FCoverEdgeHit TargetEdgeHit;
};