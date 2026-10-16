// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverSubsystem.h"

#include "Emberfall/Core/EmberfallLog.h"
#include "Emberfall/Gameplay/World/Cover/CoverObject.h"
#include "Emberfall/Gameplay/World/Cover/CoverPath.h"

#include "Kismet/GameplayStatics.h"


TWeakObjectPtr<UCoverPath> UCoverSubsystem::GetCoverPath(ACoverObject& CoverObject)
{
    // Check if UCoverPath already exists
    const TObjectPtr<UCoverPath>* Found = CoverPathsByObject.Find(&CoverObject);
    if (Found != nullptr)
    {
        return *Found;
    }

    FVector Start = FVector::ZeroVector;
    FVector End = FVector::ZeroVector;
    if (!CoverObject.TryGetLineEnds(Start, End))
    {
        UE_LOG(LogEmberfall, Warning, TEXT("%s: %s has no valid cover line."), *GetNameSafe(this), *GetNameSafe(&CoverObject));
        return {};
    }

    // The requested wall is the seed; entries in the map also mark walls as already used
    UCoverPath* Path = NewObject<UCoverPath>(this);
    CoverPathsByObject.Add(&CoverObject, Path);

    TArray<TWeakObjectPtr<ACoverObject>> OrderedWalls{};
    OrderedWalls.Add(&CoverObject);

    FVector FreeEnd;

    // Walk forward from the end of the seed wall, append neighbors at the back
    {
        const ACoverObject* Current = &CoverObject;
        FVector OpenEnd = End;

        while (ACoverObject* Next = FindNeighbor(*Current, OpenEnd, FreeEnd))
        {
            OrderedWalls.Add(Next);
            CoverPathsByObject.Add(Next, Path);

            Current = Next;
            OpenEnd = FreeEnd;
        }
    }

    // Walk backward from the start of the seed wall, prepend neighbors at the front
    {
        const ACoverObject* Current = &CoverObject;
        FVector OpenEnd = Start;

        while (ACoverObject* Next = FindNeighbor(*Current, OpenEnd, FreeEnd))
        {
            OrderedWalls.Insert(Next, 0);
            CoverPathsByObject.Add(Next, Path);

            Current = Next;
            OpenEnd = FreeEnd;
        }
    }

    Path->Initialize(OrderedWalls);
    
    UE_LOG(LogEmberfall, Log, TEXT("%s: path for %s has %d walls, length %.0f cm."),
           *GetNameSafe(this), *GetNameSafe(&CoverObject), OrderedWalls.Num(), Path->GetLength());
    return Path;
}

void UCoverSubsystem::OnWorldBeginPlay(UWorld& InWorld)
{
    Super::OnWorldBeginPlay(InWorld);
    
    TArray<AActor*> FoundActors{};
    UGameplayStatics::GetAllActorsOfClass(&InWorld, ACoverObject::StaticClass(), FoundActors);
    
    CoverObjects.Reset();
    for (AActor* Actor : FoundActors)
    {
        if (ACoverObject* Cover = Cast<ACoverObject>(Actor))
        {
            CoverObjects.Add(Cover);
        }
    }
    
    UE_LOG(LogEmberfall, Log, TEXT("%s: %d cover objects found."), *GetNameSafe(this), CoverObjects.Num());
}

ACoverObject* UCoverSubsystem::FindNeighbor(const ACoverObject& Current, const FVector& OpenEnd, FVector& OutFreeEnd) const
{
    constexpr float ThresholdSq = 10.0f * 10.0f;

    ACoverObject* Best = nullptr;
    float BestDistSq = ThresholdSq;

    for (const TWeakObjectPtr<ACoverObject>& Object : CoverObjects)
    {
        // Walls already in a path (including the ones we came from) are skipped
        if (!Object.IsValid() || Object.Get() == &Current || CoverPathsByObject.Contains(Object))
        {
            continue;
        }

        // Back-to-back walls have opposing dock normals, only walls facing the same way continue each other
        if (FVector::DotProduct(Current.GetDockNormal(), Object->GetDockNormal()) < 0.7f)
        {
            continue;
        }

        FVector OtherStart = FVector::ZeroVector;
        FVector OtherEnd = FVector::ZeroVector;
        if (!Object->TryGetLineEnds(OtherStart, OtherEnd))
        {
            continue;
        }

        const float StartDistSq = FVector::DistSquared(OpenEnd, OtherStart);
        const float EndDistSq = FVector::DistSquared(OpenEnd, OtherEnd);

        // The end that touches is the join, the other one is where the search continues
        if (StartDistSq <= BestDistSq)
        {
            BestDistSq = StartDistSq;
            Best = Object.Get();
            OutFreeEnd = OtherEnd;
        }
        if (EndDistSq <= BestDistSq)
        {
            BestDistSq = EndDistSq;
            Best = Object.Get();
            OutFreeEnd = OtherStart;
        }
    }

    return Best;
}