// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "CoverSubsystem.generated.h"

class UCoverPath;
class ACoverObject;


/**
 * @brief Collects all cover walls of a level and hands out the @c UCoverPath a wall belongs to.
 */
UCLASS()
class EMBERFALL_API UCoverSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()
    
public:
    /**
     * @brief Returns the path the given wall belongs to; builds it on first request.
     * @param CoverObject Wall hit by the cover trace.
     * @return The @c UCoverPath of the wall, owned by the subsystem, or an invalid pointer if the wall has no valid cover line.
     */
    TWeakObjectPtr<UCoverPath> GetCoverPath(ACoverObject& CoverObject);
    
    /**
     * @brief Collects all @c ACoverObject of the world.
     * @param InWorld The world that just began play.
     */
    virtual void OnWorldBeginPlay(UWorld& InWorld) override;
    
private:
    /**
     * @brief Finds the wall that continues the given wall at one of its ends.
     * @param Current Wall to continue.
     * @param OpenEnd World-space end of @c Current that is searched for a neighbor.
     * @param OutFreeEnd Receives the end of the neighbor that does not touch @c OpenEnd.
     * @return The closest unused wall facing the same way, or @c nullptr if there is none.
     */
    ACoverObject* FindNeighbor(const ACoverObject& Current, const FVector& OpenEnd, FVector& OutFreeEnd) const;
    
private:
    /** @brief All @c ACoverObject found in the world; owned by the level. */
    TSet<TWeakObjectPtr<ACoverObject>> CoverObjects{};

    /** @brief Maps each wall to the @c UCoverPath it belongs to; owns the paths so they survive garbage collection. */
    UPROPERTY()
    TMap<TWeakObjectPtr<ACoverObject>, TObjectPtr<UCoverPath>> CoverPathsByObject{};
};
