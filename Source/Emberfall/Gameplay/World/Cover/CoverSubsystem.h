// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"

#include "Emberfall/Core/Geometry/Polyline2D.h"
#include "Emberfall/Gameplay/World/Cover/CoverGroup.h"
#include "Emberfall/Gameplay/World/Cover/CoverObject.h"
#include "Emberfall/Gameplay/World/Cover/CoverSpatialGrid.h"

#include "CoverSubsystem.generated.h"


/**
 * @brief Owns the registry of all cover objects in a world, the spatial index over them and the derived groups.
 */
UCLASS()
class EMBERFALL_API UCoverSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    /**
     * @brief Creates the spatial grid from the cover settings.
     * @param Collection is the collection this subsystem belongs to.
     */
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    /**
     * @brief Releases the spatial grid and clears the registry and the groups.
     */
    virtual void Deinitialize() override;

    /**
     * @brief Registers all cover objects already placed in the world, builds the groups and draws the debug visuals.
     * @param InWorld is the world that begins play.
     */
    virtual void OnWorldBeginPlay(UWorld& InWorld) override;

    /**
     * @brief Gives read access to the cover settings this subsystem was initialized with.
     * @return The cover settings, valid between @c Initialize and @c Deinitialize.
     */
    const UCoverSettings& GetSettings() const;
    
    /**
     * @brief Adds a cover object to the registry and the spatial grid.
     * @param CoverObject is the cover object to register.
     * @return @c true if it was newly added, @c false if invalid or already registered.
     */
    bool RegisterCoverObject(ACoverObject* CoverObject);

    /**
     * @brief Removes a cover object from the registry and the spatial grid.
     * @param CoverObject is the cover object to unregister.
     * @return @c true if it was registered and got removed, otherwise @c false.
     */
    bool UnregisterCoverObject(ACoverObject* CoverObject);

    /**
     * @brief Collects the candidate cover objects in all grid cells touched by the query square.
     * @param Position is the center of the query square in world space.
     * @param Radius is the half edge length of the query square in cm.
     * @param OutCoverObjects is filled with each found object once.
     */
    void QueryCoverObjectsInGrid(const FVector& Position, float Radius,
                                 TArray<ACoverObject*>& OutCoverObjects) const;

    /**
     * @brief Collects the cover objects whose footprint lies within a distance of a position.
     * @param Position is the query point in world space.
     * @param MaxDistance is the maximum distance from the position to the footprint in cm.
     * @param OutCoverObjects is filled with each matching object once.
     */
    void QueryCoverObjectsInDistance(const FVector& Position, float MaxDistance,
                                     TArray<ACoverObject*>& OutCoverObjects) const;

    /**
     * @brief Collects every enabled footprint edge within a distance of a position.
     * @param Position is the query point in world space in cm.
     * @param MaxDistance is the maximum distance from the position to the edge in cm.
     * @param OutHits is filled with one entry per matching edge, unordered.
     */
    void QueryCoverEdgesInDistance(const FVector& Position, float MaxDistance, TArray<FCoverEdgeHit>& OutHits) const;

    /**
     * @brief Finds the closest enabled footprint edge within a distance of a position.
     * @param Position is the query point in world space in cm.
     * @param MaxDistance is the maximum distance from the position to the edge in cm.
     * @param OutHit is filled with the closest edge.
     * @return @c true if an enabled edge was found, otherwise @c false.
     */
    bool FindNearestCoverEdge(const FVector& Position, float MaxDistance, FCoverEdgeHit& OutHit) const;

    /**
     * @brief Finds the outline path a cover object belongs to, the loop of its group that lies closest to a position.
     * @param CoverObject is the cover object whose group is searched.
     * @param Position is the point the loop is chosen by in the ground plane in cm.
     * @param OutPath is filled with the chosen loop as a polyline in the ground plane.
     * @return @c true if the group has a loop and @c OutPath was filled, otherwise @c false.
     */
    bool FindCoverPath(const ACoverObject* CoverObject, const FVector2D& Position, FPolyline2D& OutPath) const;

    /**
     * @brief Rebuilds all groups from the registered cover objects.
     */
    void RebuildGroups();

    /**
     * @brief Gives read access to the current groups.
     * @return All groups, every registered object is in exactly one of them.
     */
    const TArray<FCoverGroup>& GetGroups();

    /**
     * @brief Marks the groups as outdated and schedules one rebuild for the next tick.
     */
    void MarkGroupsDirty();
    
#if ENABLE_DRAW_DEBUG
    /**
     * @brief Draws the occupied grid cells and the group footprints for visual verification.
     * @param Duration is the lifetime of the shapes in seconds, @c -1 keeps them until the world ends.
     */
    void DrawDebug(float Duration);
#endif

private:
    /**
     * @brief Finds all cover objects currently placed in the world.
     * @param OutCoverObjects is filled with all found @c ACoverObject instances.
     */
    void CollectCoverObjects(TArray<ACoverObject*>& OutCoverObjects) const;

    /**
     * @brief Moves a cover object to the cells of its new position and marks the groups as outdated.
     * @param CoverObject is the object whose transform changed.
     */
    void HandleCoverObjectChanged(ACoverObject* CoverObject);

    /** @brief All currently registered cover objects. */
    UPROPERTY()
    TSet<TObjectPtr<ACoverObject>> CoverObjects;

    /** @brief Cover settings the subsystem works with, not owned, valid between @c Initialize and @c Deinitialize. */
    UPROPERTY()
    const UCoverSettings* Settings{ nullptr };
    
    /** @brief Spatial index over all registered cover objects, valid between @c Initialize and @c Deinitialize. */
    TUniquePtr<FCoverSpatialGrid> SpatialGrid;

    /** @brief Groups derived from the registry by @c RebuildGroups, never the source of truth. */
    TArray<FCoverGroup> Groups;

    /** @brief Whether the groups are outdated and must be rebuilt before the next read. */
    bool bGroupsDirty{false};
};
