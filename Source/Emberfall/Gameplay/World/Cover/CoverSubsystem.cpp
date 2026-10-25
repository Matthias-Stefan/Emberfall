// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverSubsystem.h"
#include "Emberfall/Gameplay/World/Cover/CoverObject.h"
#include "Emberfall/Gameplay/World/Cover/CoverPath.h"

#include "EngineUtils.h"


TWeakObjectPtr<UCoverPath> UCoverSubsystem::GetCoverPath(ACoverObject& CoverObject, const FVector& SurfaceNormal)
{
    FCoverRun Run{};
    int32 RunId = INDEX_NONE;
    if (!CoverObject.TryGetRunForNormal(SurfaceNormal, Run, RunId))
    {
        return {};
    }

    const TWeakObjectPtr<UCoverPath>* Found = PathsByRun.Find(FCoverRunKey(&CoverObject, RunId));
    return Found != nullptr ? *Found : TWeakObjectPtr<UCoverPath>{};
}

void UCoverSubsystem::OnWorldBeginPlay(UWorld& InWorld)
{
    Super::OnWorldBeginPlay(InWorld);

    for (TActorIterator<ACoverObject> It(&InWorld); It; ++It)
    {
        ACoverObject* CoverObject = *It;
        CoverObject->OnActiveSidesChanged.AddUObject(this, &UCoverSubsystem::ActiveSidesChanged);
        BuildPaths(*CoverObject);
    }
}

void UCoverSubsystem::BuildPaths(ACoverObject& CoverObject)
{
    TArray<FCoverRun> Runs;
    CoverObject.GetRuns(Runs);

    for (const FCoverRun& Run : Runs)
    {
        UCoverPath* Path = NewObject<UCoverPath>(this);
        Path->Initialize(Run);
        Paths.Add(Path);
        PathsByRun.Add(FCoverRunKey(&CoverObject, Run.EdgeIds[0]), Path);
    }
}

void UCoverSubsystem::ActiveSidesChanged(ACoverObject& CoverObject)
{
    for (auto It = PathsByRun.CreateIterator(); It; ++It)
    {
        if (It.Key().Key == &CoverObject)
        {
            It.RemoveCurrent();
        }
    }

    BuildPaths(CoverObject);
}

