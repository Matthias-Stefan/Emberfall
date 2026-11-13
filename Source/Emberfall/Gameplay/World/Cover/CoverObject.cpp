// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverObject.h"

#include "Emberfall/Gameplay/World/Cover/CoverGeometry.h"
#include "Emberfall/Gameplay/World/Cover/CoverLog.h"
#include "Emberfall/Gameplay/World/Cover/CoverSidesComponent.h"
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

#if WITH_EDITORONLY_DATA
    SidesVisualizer = CreateDefaultSubobject<UCoverSidesComponent>(TEXT("SidesVisualizer"));
    SidesVisualizer->SetupAttachment(CoverMesh);
#endif
}

void ACoverObject::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);

    if (!BuildPerimeter())
    {
        UE_LOG(LogCover, Warning, TEXT("ACoverObject '%s': BuildPerimeter failed, no static mesh set"), *GetName());
    }
}

#if WITH_EDITOR
void ACoverObject::PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent)
{
    Super::PostEditChangeProperty(PropertyChangedEvent);

    if (PropertyChangedEvent.GetPropertyName() != GET_MEMBER_NAME_CHECKED(ACoverObject, EnabledSides))
    {
        return;
    }

    OnChanged.Broadcast(this);

    // The proxy holds a copy of the edge colors, so it has to be built again.
    if (SidesVisualizer)
    {
        SidesVisualizer->MarkRenderStateDirty();
    }
}
#endif

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

    // Order: positive signed area in the XY plane, unless the actor is mirrored by a negative scale.
    OutCorners.Reset(4);
    OutCorners.Add(MeshTransform.TransformPosition(FVector(LocalCenter.X - HalfX, LocalCenter.Y - HalfY, BottomZ)));
    OutCorners.Add(MeshTransform.TransformPosition(FVector(LocalCenter.X + HalfX, LocalCenter.Y - HalfY, BottomZ)));
    OutCorners.Add(MeshTransform.TransformPosition(FVector(LocalCenter.X + HalfX, LocalCenter.Y + HalfY, BottomZ)));
    OutCorners.Add(MeshTransform.TransformPosition(FVector(LocalCenter.X - HalfX, LocalCenter.Y + HalfY, BottomZ)));
    return true;
}

bool ACoverObject::GetFootprintEdges(TArray<FVector>& OutCorners, TArray<bool>& OutEdgeEnabled) const
{
    if (!GetFootprintCorners(OutCorners))
    {
        return false;
    }

    FVector2D AxisX;
    FVector2D AxisY;
    GetSideAxes(AxisX, AxisY);
    const ECoverSide Enabled = GetEnabledSides();

    FVector Center = FVector::ZeroVector;
    for (const FVector& Corner : OutCorners)
    {
        Center += Corner;
    }
    Center /= OutCorners.Num();

    OutEdgeEnabled.Reset(OutCorners.Num());
    for (int32 CornerIndex = 0; CornerIndex < OutCorners.Num(); ++CornerIndex)
    {
        // The normal points from the center to the edge middle, so it does not depend on the winding.
        const FVector EdgeMiddle = (OutCorners[CornerIndex] + OutCorners[(CornerIndex + 1) % OutCorners.Num()]) * 0.5;
        const FVector2D OutwardNormal = FVector2D(EdgeMiddle.X - Center.X, EdgeMiddle.Y - Center.Y).GetSafeNormal();

        const ECoverSide Side = FCoverGeometry::ClassifySide2D(OutwardNormal, AxisX, AxisY);
        OutEdgeEnabled.Add(EnumHasAnyFlags(Enabled, Side));
    }
    return true;
}

ECoverSide ACoverObject::GetEnabledSides() const
{
    return static_cast<ECoverSide>(EnabledSides & static_cast<int32>(ECoverSide::All));
}

void ACoverObject::SetEnabledSides(ECoverSide NewSides)
{
    const int32 NewMask = static_cast<int32>(NewSides);
    if (EnabledSides == NewMask)
    {
        return;
    }

    EnabledSides = NewMask;
    OnChanged.Broadcast(this);

#if WITH_EDITORONLY_DATA
    if (SidesVisualizer)
    {
        SidesVisualizer->MarkRenderStateDirty();
    }
#endif
}

void ACoverObject::GetSideAxes(FVector2D& OutAxisX, FVector2D& OutAxisY) const
{
    const FTransform& MeshTransform = CoverMesh->GetComponentTransform();

    // TransformVector keeps the scale, so a negative scale mirrors the axis. That is intended:
    // the local +X side then really faces the other way in the world.
    const FVector WorldAxisX = MeshTransform.TransformVector(FVector::XAxisVector);
    const FVector WorldAxisY = MeshTransform.TransformVector(FVector::YAxisVector);

    OutAxisX = FVector2D(WorldAxisX.X, WorldAxisX.Y).GetSafeNormal();
    OutAxisY = FVector2D(WorldAxisY.X, WorldAxisY.Y).GetSafeNormal();
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