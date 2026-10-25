#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "CoverSubsystem.generated.h"

class UCoverPath;
class ACoverObject;


/**
 * @brief Hands out the @c UCoverPath of the run a cover trace hit; builds paths on first request.
 */
UCLASS()
class EMBERFALL_API UCoverSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    /**
     * @brief Returns the path of the run that faces the given surface normal.
     * @param CoverObject Object hit by the cover trace.
     * @param SurfaceNormal Normal of the surface hit by the trace.
     * @return The @c UCoverPath, or an invalid pointer if no active edge faces the normal.
     */
    TWeakObjectPtr<UCoverPath> GetCoverPath(ACoverObject& CoverObject, const FVector& SurfaceNormal);

    /**
     * @brief Collects all cover objects, binds their change delegate and builds their paths.
     * @param InWorld The world that begins play.
     */
    virtual void OnWorldBeginPlay(UWorld& InWorld) override;

private:
    /**
     * @brief Builds one path per run of a cover object and stores it in @c PathsByRun.
     * @param CoverObject The object to build the paths for.
     */
    void BuildPaths(ACoverObject& CoverObject);

    /**
     * @brief Drops all cached paths of a cover object after its active sides changed.
     * @param CoverObject The object whose @c ActiveSides changed.
     */
    void ActiveSidesChanged(ACoverObject& CoverObject);

private:
    /** @brief Object and run id inside it. */
    using FCoverRunKey = TPair<TWeakObjectPtr<ACoverObject>, int32>;

private:
    /** @brief Built paths by run. */
    TMap<FCoverRunKey, TWeakObjectPtr<UCoverPath>> PathsByRun{};

    /** @brief Owns all built paths so they survive garbage collection. */
    UPROPERTY()
    TArray<TObjectPtr<UCoverPath>> Paths{};
};
