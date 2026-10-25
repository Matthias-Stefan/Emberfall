// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverObject.h"
#include "Emberfall/Gameplay/World/Cover/CoverObjectTypes.h"

#include "Components/SplineComponent.h"


ACoverObject::ACoverObject()
{
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    SetRootComponent(Mesh);
    Mesh->SetCollisionResponseToChannel(ECC_COVER, ECR_Block);

    OutlineLine = CreateDefaultSubobject<USplineComponent>(TEXT("OutlineLine"));
    OutlineLine->SetupAttachment(Mesh);
    OutlineLine->SetClosedLoop(true, false);

    PrimaryActorTick.bCanEverTick = true;
}

void ACoverObject::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);

    if (bAutoFitOutline)
    {
        FitOutline();
    }
}

void ACoverObject::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    DrawDebugRuns();
}

bool ACoverObject::ShouldTickIfViewportsOnly() const
{
    return true;
}

#if WITH_EDITOR
void ACoverObject::PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent)
{
    Super::PostEditChangeProperty(PropertyChangedEvent);

    if (PropertyChangedEvent.GetPropertyName() == GET_MEMBER_NAME_CHECKED(ACoverObject, ActiveSides))
    {
        OnActiveSidesChanged.Broadcast(*this);
    }
}
#endif

void ACoverObject::GetRuns(TArray<FCoverRun>& OutRuns) const
{
    OutRuns.Reset();

    if (OutlineLine == nullptr || OutlineLine->GetNumberOfSplinePoints() != 4)
    {
        return;
    }

    FVector Points[4];
    for (int32 Index = 0; Index < 4; ++Index)
    {
        Points[Index] = OutlineLine->GetLocationAtSplinePoint(Index, ESplineCoordinateSpace::World);
    }

    // Edge i runs from point i to point i + 1; counter-clockwise, so the outward normal is the edge direction rotated by -90 degrees
    FVector Normals[4];
    for (int32 Index = 0; Index < 4; ++Index)
    {
        const FVector Direction = (Points[(Index + 1) % 4] - Points[Index]).GetSafeNormal2D();
        Normals[Index] = FVector(Direction.Y, -Direction.X, 0.0f);
    }

    auto IsActive = [this](int32 Edge) { return (ActiveSides & (1 << Edge)) != 0; };

    // All edges active: one closed run
    if (ActiveSides == static_cast<int32>(ECoverSide::All))
    {
        FCoverRun& Run = OutRuns.AddDefaulted_GetRef();
        Run.bClosed = true;
        for (int32 Index = 0; Index < 4; ++Index)
        {
            Run.Points.Add(Points[Index]);
            Run.EdgeNormals.Add(Normals[Index]);
            Run.EdgeIds.Add(Index);
        }
        return;
    }

    // Start right after a blocked edge, so no run is split by the array wrap-around
    int32 FirstBlocked = INDEX_NONE;
    for (int32 Index = 0; Index < 4; ++Index)
    {
        if (!IsActive(Index))
        {
            FirstBlocked = Index;
            break;
        }
    }
    if (FirstBlocked == INDEX_NONE)
    {
        return;
    }

    FCoverRun* Current = nullptr;
    for (int32 Step = 1; Step <= 4; ++Step)
    {
        const int32 Edge = (FirstBlocked + Step) % 4;
        if (!IsActive(Edge))
        {
            Current = nullptr;
            continue;
        }

        if (Current == nullptr)
        {
            Current = &OutRuns.AddDefaulted_GetRef();
            Current->Points.Add(Points[Edge]);
        }
        Current->Points.Add(Points[(Edge + 1) % 4]);
        Current->EdgeNormals.Add(Normals[Edge]);
        Current->EdgeIds.Add(Edge);
    }
}

bool ACoverObject::TryGetRunForNormal(const FVector& SurfaceNormal, FCoverRun& OutRun, int32& OutRunId) const
{
    TArray<FCoverRun> Runs;
    GetRuns(Runs);

    for (const FCoverRun& Run : Runs)
    {
        for (const FVector& EdgeNormal : Run.EdgeNormals)
        {
            if (FVector::DotProduct(EdgeNormal, SurfaceNormal) > 0.7f)
            {
                OutRun = Run;
                OutRunId = Run.EdgeIds[0];
                return true;
            }
        }
    }
    return false;
}

void ACoverObject::SetActiveSides(ECoverSide NewActiveSides)
{
    const int32 NewValue = static_cast<int32>(NewActiveSides);
    if (ActiveSides == NewValue)
    {
        return;
    }

    ActiveSides = NewValue;
    OnActiveSidesChanged.Broadcast(*this);
}

void ACoverObject::FitOutline()
{
    const UStaticMesh* StaticMesh = Mesh->GetStaticMesh();
    if (StaticMesh == nullptr)
    {
        return;
    }

    const FBox Box = StaticMesh->GetBoundingBox();

    // The spline inherits the mesh scale, so convert the world-space offset to local space
    const FVector Scale = Mesh->GetComponentScale().GetAbs().ComponentMax(FVector(UE_KINDA_SMALL_NUMBER));
    const float MinX = Box.Min.X - LineOffset / Scale.X;
    const float MaxX = Box.Max.X + LineOffset / Scale.X;
    const float MinY = Box.Min.Y - LineOffset / Scale.Y;
    const float MaxY = Box.Max.Y + LineOffset / Scale.Y;
    const float Z = Box.GetCenter().Z;

    // Counter-clockwise seen from above; edges: -Y, +X, +Y, -X
    const FVector Corners[4] =
    {
        {MinX, MinY, Z},
        {MaxX, MinY, Z},
        {MaxX, MaxY, Z},
        {MinX, MaxY, Z},
    };

    OutlineLine->ClearSplinePoints(false);
    for (const FVector& Corner : Corners)
    {
        OutlineLine->AddSplinePoint(Corner, ESplineCoordinateSpace::Local, false);
    }
    for (int32 Index = 0; Index < 4; ++Index)
    {
        OutlineLine->SetSplinePointType(Index, ESplinePointType::Linear, false);
    }
    OutlineLine->SetClosedLoop(true, true);
}

void ACoverObject::DrawDebugRuns() const
{
    if (!bDrawDebugRuns || OutlineLine == nullptr || OutlineLine->GetNumberOfSplinePoints() != 4)
    {
        return;
    }

    FVector Points[4];
    for (int32 Index = 0; Index < 4; ++Index)
    {
        Points[Index] = OutlineLine->GetLocationAtSplinePoint(Index, ESplineCoordinateSpace::World);
    }

    // Blocked edges red, active edges get a normal arrow
    for (int32 Edge = 0; Edge < 4; ++Edge)
    {
        const FVector From = Points[Edge];
        const FVector To = Points[(Edge + 1) % 4];

        if ((ActiveSides & (1 << Edge)) == 0)
        {
            DrawDebugLine(GetWorld(), From, To, FColor::Red, false, -1.0f, 0, 4.0f);
            continue;
        }

        const FVector Direction = (To - From).GetSafeNormal2D();
        const FVector Normal(Direction.Y, -Direction.X, 0.0f);
        const FVector Mid = (From + To) * 0.5f;
        DrawDebugDirectionalArrow(GetWorld(), Mid, Mid + Normal * 50.0f, 20.0f, FColor::Green, false, -1.0f, 0, 2.0f);
    }
}
