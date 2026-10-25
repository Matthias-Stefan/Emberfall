// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "Emberfall/Gameplay/World/Cover/CoverObjectTypes.h"

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CoverObject.generated.h"

class ACoverObject;
class USplineComponent;
struct FCoverRun;


/** @brief Fired after @c ActiveSides changed at runtime. */
DECLARE_MULTICAST_DELEGATE_OneParam(FOnCoverActiveSidesChanged, ACoverObject&);

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
     * @brief Draws the debug runs every frame.
     * @param DeltaSeconds Seconds since the last frame.
     */
    virtual void Tick(float DeltaSeconds) override;

    /**
     * @brief Keeps the actor ticking in editor viewports so the debug lines update live.
     * @return Always @c true.
     */
    virtual bool ShouldTickIfViewportsOnly() const override;
    
#if WITH_EDITOR
    /**
     * @brief Notifies listeners when @c ActiveSides was edited in the details panel.
     * @param PropertyChangedEvent The property that was edited.
     */
    virtual void PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent) override;
#endif
    
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

    /**
     * @brief Sets the active sides and notifies listeners if the value changed.
     * @param NewActiveSides Sides that offer cover, combined with @c | .
     */
    void SetActiveSides(ECoverSide NewActiveSides);

    /**
     * @brief Returns the sides that offer cover.
     * @return Active sides as @c ECoverSide flags.
     */
    ECoverSide GetActiveSides() const { return static_cast<ECoverSide>(ActiveSides); }

public:
    /** @brief Fired by @c SetActiveSides; the cover subsystem uses it to drop cached paths. */
    FOnCoverActiveSidesChanged OnActiveSidesChanged;
    
private:
    /** @brief Rebuilds @c OutlineLine as a closed rectangle around the mesh bounds. */
    void FitOutline();
    
    /** @brief Draws active edges green (closed run) or yellow (open run), blocked edges red, plus the edge normals. */
    void DrawDebugRuns() const;
    
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

    /** @brief Closed loop around the mesh; the edge at index N runs from spline point N to point N + 1, in the order of @c ECoverSide. */
    UPROPERTY(VisibleAnywhere, Category = "Cover")
    TObjectPtr<USplineComponent> OutlineLine;
    
    /** @brief Draws the runs and their normals for debugging. */
    UPROPERTY(EditAnywhere, Category = "Cover|Debug")
    bool bDrawDebugRuns = true;
};