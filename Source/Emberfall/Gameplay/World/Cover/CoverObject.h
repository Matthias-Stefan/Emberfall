// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "Emberfall/Gameplay/World/Cover/CoverObjectTypes.h"

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CoverObject.generated.h"

struct FCoverRun;
class USplineComponent;


/**
 * @brief Anything a unit can take cover behind or lean against.
 */
UCLASS()
class EMBERFALL_API ACoverObject : public AActor
{
    GENERATED_BODY()

public:
    ACoverObject();

    /**
     * @brief Refits the outline to the mesh bounds when @c bAutoFitOutline is set.
     * @param Transform Actor transform used for construction.
     */
    virtual void OnConstruction(const FTransform& Transform) override;

    /**
     * @brief Returns the height class of this cover.
     * @return @c ECoverHeight of the object.
     */
    ECoverHeight GetCoverHeight() const { return CoverHeight; }
    
    /**
     * @brief Derives the walkable runs from @c OutlineLine and @c ActiveSides.
     * @param OutRuns Receives the runs (cleared first).
     */
    void GetRuns(TArray<FCoverRun>& OutRuns) const;

    /**
     * @brief Finds the active run that has an edge facing the given surface normal.
     * @param SurfaceNormal Normal of the surface hit by the cover trace.
     * @param OutRun Receives the run.
     * @param OutRunId Receives the id of the run within this object.
     * @return @c true if an active edge faces the normal, otherwise @c false.
     */
    bool TryGetRunForNormal(const FVector& SurfaceNormal, FCoverRun& OutRun, int32& OutRunId) const;

private:
    /** @brief Rebuilds @c OutlineLine as a closed rectangle around the mesh bounds. */
    void FitOutline();

protected:
    /** @brief Visual mesh of the cover object, blocks the @c Cover trace channel. */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Cover", meta = (AllowPrivateAccess = "true"))
    TObjectPtr<UStaticMeshComponent> Mesh;

    /** @brief Height class of the cover, decides crouch vs. stand animation. */
    UPROPERTY(EditAnywhere, Category = "Cover")
    ECoverHeight CoverHeight = ECoverHeight::Low;

    /** @brief When @c true the outline is rebuilt from the mesh bounds on every construction, overwriting manual edits. */
    UPROPERTY(EditAnywhere, Category = "Cover")
    bool bAutoFitOutline = true;

    /** @brief Distance in cm (world units) the outline is moved outwards from the mesh bounds. */
    UPROPERTY(EditAnywhere, Category = "Cover")
    float LineOffset = 30.0f;

    /** @brief Sides that offer cover; deactivate a side for windows, doors or a wall behind it. */
    UPROPERTY(EditAnywhere, Category = "Cover", meta = (Bitmask, BitmaskEnum = "/Script/Emberfall.ECoverSide"))
    int32 ActiveSides{ static_cast<int32>(ECoverSide::All) };

    /** @brief Closed loop around the mesh; edge @c i runs from point @c i to point @c i + 1 (see @c ECoverSide order). */
    UPROPERTY(VisibleAnywhere, Category = "Cover")
    TObjectPtr<USplineComponent> OutlineLine;
};