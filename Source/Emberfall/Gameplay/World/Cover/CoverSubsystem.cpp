// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverSubsystem.h"

#include "Emberfall/Core/EmberfallLog.h"
#include "Emberfall/Gameplay/World/Cover/CoverObject.h"
#include "Emberfall/Gameplay/World/Cover/CoverPath.h"

#include "Kismet/GameplayStatics.h"


TWeakObjectPtr<UCoverPath> UCoverSubsystem::GetCoverPath(ACoverObject& CoverObject, const FVector& SurfaceNormal)
{
    FCoverRun Run{};
    int32 RunId = INDEX_NONE;
    if (!CoverObject.TryGetRunForNormal(SurfaceNormal, Run, RunId))
    {
        return {};
    }

    const FCoverRunKey Key(&CoverObject, RunId);
    if (const TWeakObjectPtr<UCoverPath>* Found = PathsByRun.Find(Key))
    {
        return *Found;
    }

    UCoverPath* Path = NewObject<UCoverPath>(this);
    Path->Initialize(Run);
    Paths.Add(Path);
    PathsByRun.Add(Key, Path);
    return Path;
}

