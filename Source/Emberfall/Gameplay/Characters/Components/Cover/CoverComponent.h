// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "Emberfall/Gameplay/Characters/Components/Cover/CoverComponentTypes.h"

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "CoverComponent.generated.h"

class USplineComponent;


/** @brief Tracks the cover a unit is docked to. */
UCLASS(ClassGroup=(Emberfall), meta=(BlueprintSpawnableComponent))
class EMBERFALL_API UCoverComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    /** @brief Default constructor. */
    UCoverComponent();

    /**
     * @brief Advances the dock slide and switches to @c ECoverState::InCover once it is finished.
     * @param DeltaTime Seconds since the last frame.
     * @param TickType Kind of tick this is.
     * @param ThisTickFunction Tick function that triggered this call.
     */
    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
                               FActorComponentTickFunction* ThisTickFunction) override;

    /**
     * @brief Projects a move target onto the cover line the unit is docked to.
     * @param Target Requested world location.
     * @return @c Target projected onto the cover line, the current location while docking,
     *         or @c Target unchanged if the unit is not in cover.
     */
    FVector ConstrainToCover(const FVector& Target) const;

    /**
     * @brief Traces forward on the @c ECC_Cover channel and enters cover if a @c ACoverObject is in reach.
     * @return @c true if cover was entered.
     */
    UFUNCTION(BlueprintCallable, Category = "Cover")
    bool TryEnterCover();

    /** @brief Leaves cover and resets the state machine to @c ECoverState::None. */
    UFUNCTION(BlueprintCallable, Category = "Cover")
    void LeaveCover();

    /**
     * @brief Returns the dock normal of the current cover.
     * @return World-space normal pointing away from the wall, or @c FVector::ZeroVector if not in cover.
     */
    UFUNCTION(BlueprintPure, Category = "Cover")
    FVector GetCoverNormal() const { return CoverNormal; }

    /**
     * @brief Returns the current phase of the cover state machine.
     * @return Current @c ECoverState.
     */
    UFUNCTION(BlueprintPure, Category = "Cover")
    ECoverState GetCoverState() const { return CoverState; }

    /**
     * @brief Returns whether the unit is docked and can move along the cover line.
     * @return @c true while @c CoverState is @c ECoverState::InCover.
     */
    UFUNCTION(BlueprintPure, Category = "Cover")
    bool IsInCover() const { return CoverState == ECoverState::InCover; }

    /**
     * @brief Returns whether the unit is sliding onto the cover line.
     * @return @c true while @c CoverState is @c ECoverState::Docking.
     */
    UFUNCTION(BlueprintPure, Category = "Cover")
    bool IsDocking() const { return CoverState == ECoverState::Docking; }

    /**
     * @brief Returns the runtime data of the current dock slide.
     * @return Read-only reference to the @c FCoverDockData.
     */
    const FCoverDockData& GetDockData() const { return DockData; }

protected:
    /** @brief Reach of the cover trace in cm, measured from the unit center along its forward vector. */
    UPROPERTY(EditDefaultsOnly, Category = "Cover", meta = (ClampMin = "1", Units = "cm"))
    float CoverTraceDistance{150.0f};
    
    /** @brief Duration in seconds of the slide onto the cover line. */
    UPROPERTY(EditDefaultsOnly, Category = "Cover", meta = (ClampMin = "0.01", Units = "s"))
    float DockDuration{0.25f};
    
    /** @brief Distance in cm the mesh is shifted towards the wall while in cover. */
    UPROPERTY(EditDefaultsOnly, Category = "Cover", meta = (ClampMin = "0", Units = "cm"))
    float CoverMeshOffset{ 14.0f };

private:
    /** @brief Spline of the cover the unit is docked to. */
    TWeakObjectPtr<USplineComponent> Spline{};

    /** @brief Dock normal of the current cover, points away from the wall. */
    FVector CoverNormal{FVector::ZeroVector};

    /** @brief Current phase of the cover state machine. */
    ECoverState CoverState{ECoverState::None};

    /** @brief Runtime data of the current dock slide. */
    FCoverDockData DockData;
};
