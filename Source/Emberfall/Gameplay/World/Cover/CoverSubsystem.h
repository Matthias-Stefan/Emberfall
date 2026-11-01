// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "Emberfall/Gameplay/World/Cover/CoverObject.h"
#include "Emberfall/Gameplay/World/Cover/CoverSpatialGrid.h"

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "CoverSubsystem.generated.h"


/**
 * @brief Owns the registry of all cover objects in a world and the spatial index over them.
 */
UCLASS()
class EMBERFALL_API UCoverSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    /**
     * @brief Creates the spatial grid from the cover settings.
     * @param Collection The collection this subsystem belongs to.
     */
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    
    /**
     * @brief Releases the spatial grid and clears the registry.
     */
    virtual void Deinitialize() override;

    /**
     * @brief Registers all cover objects already placed in the world.
     * @param InWorld The world that begins play.
     */
    virtual void OnWorldBeginPlay(UWorld& InWorld) override;
    
    /**
     * @brief Adds a cover object to the registry.
     * @param CoverObject The cover object to register.
     * @return @c true if it was newly added, @c false if invalid or already registered.
     */
    bool RegisterCoverObject(ACoverObject* CoverObject);

    /**
     * @brief Removes a cover object from the registry.
     * @param CoverObject The cover object to unregister.
     * @return @c true if it was registered and got removed, otherwise @c false.
     */
    bool UnregisterCoverObject(ACoverObject* CoverObject);

    /**
     * @brief Collects all registered cover objects in grid cells touched by the query circle.
     * @param Position Center of the query in world space.
     * @param Radius Query radius in cm.
     * @param OutCoverObjects Receives each found object once.
     */
    void GetNearbyCoverObjects(const FVector& Position, float Radius, TArray<ACoverObject*>& OutCoverObjects) const;

#if ENABLE_DRAW_DEBUG
    /**
     * @brief Draws one box per occupied grid cell for visual verification.
     * @param Duration Lifetime of the lines in seconds, @c -1 keeps them until the world ends.
     */
    void DrawDebugCells(float Duration) const;
    
    /**
     * @brief Draws the oriented footprint of every registered cover object in blue.
     * @param Duration Lifetime of the lines in seconds, @c -1 keeps them until the world ends.
     */
    void DrawDebugFootprints(float Duration) const;
#endif
    
private:
    /**
     * @brief Finds all cover objects currently placed in the world.
     * @param OutCoverObjects Receives all found @c ACoverObject instances.
     */
    void CollectCoverObjects(TArray<ACoverObject*>& OutCoverObjects) const;

private:
    /** @brief All currently registered cover objects. */
    UPROPERTY()
    TSet<TObjectPtr<ACoverObject>> CoverObjects;

    /** @brief Spatial index over all registered cover objects; valid between @c Initialize and @c Deinitialize. */
    TUniquePtr<FCoverSpatialGrid> SpatialGrid;
};
