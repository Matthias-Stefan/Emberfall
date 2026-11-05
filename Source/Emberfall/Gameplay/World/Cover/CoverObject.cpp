// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverObject.h"
#include "Emberfall/Gameplay/World/Cover/CoverSubsystem.h"

#include "Components/SplineComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"


ACoverObject::ACoverObject()
{
    CoverMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CoverMesh"));
    SetRootComponent(CoverMesh);

    PerimeterSpline = CreateDefaultSubobject<USplineComponent>(TEXT("PerimeterSpline"));
    PerimeterSpline->SetupAttachment(CoverMesh);
}

void ACoverObject::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);

    if (!BuildPerimeter())
    {
        UE_LOG(LogTemp, Warning, TEXT("ACoverObject '%s': BuildPerimeter failed, no static mesh set"), *GetName());
    }
}

bool ACoverObject::GetFootprintCorners(TArray<FVector>& OutCorners, float ExtentScale) const
{
    const UStaticMesh* Mesh = CoverMesh->GetStaticMesh();
    if (!Mesh)
    {
        return false;
    }

    // Bounds are taken in mesh space and transformed afterwards, so rotation and scale yield an OBB instead of an AABB.
    const FBoxSphereBounds LocalBounds = Mesh->GetBounds();
    const FVector LocalCenter = LocalBounds.Origin;
    const FVector LocalExtent = LocalBounds.BoxExtent;

    const float HalfX = LocalExtent.X * ExtentScale;
    const float HalfY = LocalExtent.Y * ExtentScale;
    const float BottomZ = LocalCenter.Z - LocalExtent.Z;

    const FTransform& MeshTransform = CoverMesh->GetComponentTransform();

    // Order: counter-clockwise seen from above, unless the actor is mirrored by a negative scale.
    OutCorners.Reset(4);
    OutCorners.Add(MeshTransform.TransformPosition(FVector(LocalCenter.X - HalfX, LocalCenter.Y - HalfY, BottomZ)));
    OutCorners.Add(MeshTransform.TransformPosition(FVector(LocalCenter.X + HalfX, LocalCenter.Y - HalfY, BottomZ)));
    OutCorners.Add(MeshTransform.TransformPosition(FVector(LocalCenter.X + HalfX, LocalCenter.Y + HalfY, BottomZ)));
    OutCorners.Add(MeshTransform.TransformPosition(FVector(LocalCenter.X - HalfX, LocalCenter.Y + HalfY, BottomZ)));
    return true;
}

bool ACoverObject::BuildPerimeter() const
{
    TArray<FVector> Corners;
    if (!GetFootprintCorners(Corners, PerimeterScale))
    {
        return false;
    }

    // Height is added in world Z, which is only the footprint's "up" as long as the actor is not tilted.
    for (FVector& Corner : Corners)
    {
        Corner.Z += PerimeterHeight;
    }

    // Defer the spline update until all points are set, one rebuild at the end is enough.
    PerimeterSpline->SetSplinePoints(Corners, ESplineCoordinateSpace::World, false);
    for (int32 PointIndex = 0; PointIndex < Corners.Num(); ++PointIndex)
    {
        PerimeterSpline->SetSplinePointType(PointIndex, ESplinePointType::Linear, false);
    }
    PerimeterSpline->SetClosedLoop(true, false);
    PerimeterSpline->UpdateSpline();

    return true;
}

void ACoverObject::BeginPlay()
{
    Super::BeginPlay();

    TransformUpdatedHandle = CoverMesh->TransformUpdated.AddUObject(this, &ACoverObject::HandleMeshTransformUpdated);

    if (const UWorld* World = GetWorld(); World != nullptr)
    {
        if (UCoverSubsystem* CoverSubsystem = World->GetSubsystem<UCoverSubsystem>(); CoverSubsystem != nullptr)
        {
            CoverSubsystem->RegisterCoverObject(this);
        }
    }
}

void ACoverObject::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (const UWorld* World = GetWorld(); World != nullptr)
    {
        if (UCoverSubsystem* CoverSubsystem = World->GetSubsystem<UCoverSubsystem>(); CoverSubsystem != nullptr)
        {
            CoverSubsystem->UnregisterCoverObject(this);
        }
    }

    CoverMesh->TransformUpdated.Remove(TransformUpdatedHandle);
    TransformUpdatedHandle.Reset();

    Super::EndPlay(EndPlayReason);
}

void ACoverObject::HandleMeshTransformUpdated(USceneComponent* UpdatedComponent,
    EUpdateTransformFlags UpdateTransformFlags, ETeleportType Teleport)
{
    OnChanged.Broadcast(this);
}
