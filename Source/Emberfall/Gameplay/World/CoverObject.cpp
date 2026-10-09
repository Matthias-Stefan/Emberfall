// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/CoverObject.h"

#include "Components/SplineComponent.h"


ACoverObject::ACoverObject()
{
	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	SetRootComponent(Mesh);
	Mesh->SetCollisionResponseToChannel(ECC_COVER, ECR_Block);

	CoverLine = CreateDefaultSubobject<USplineComponent>(TEXT("CoverLine"));
	CoverLine->SetupAttachment(Mesh);

	PrimaryActorTick.bCanEverTick = false;
}

void ACoverObject::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	
	if (bAutoFitLine)
	{
		FitCoverLineToMesh();
	}
}

bool ACoverObject::CanDockFromNormal(const FVector& SurfaceNormal) const
{
	return FVector::DotProduct(SurfaceNormal, GetDockNormal()) > 0.7f;
}

void ACoverObject::FitCoverLineToMesh()
{
	const UStaticMesh* StaticMesh = Mesh->GetStaticMesh();
	if (!StaticMesh)
	{
		return;
	}

	const FBox Box = StaticMesh->GetBoundingBox();

	// The spline inherits the mesh scale, so convert the world-space offset to local space
	const float ScaleY = FMath::Max(FMath::Abs(Mesh->GetComponentScale().Y), UE_KINDA_SMALL_NUMBER);

	const float LineY = Box.Max.Y + LineOffset / ScaleY;
	const float LineZ = Box.GetCenter().Z;

	CoverLine->ClearSplinePoints(false);
	CoverLine->AddSplinePoint(FVector(Box.Min.X, LineY, LineZ), ESplineCoordinateSpace::Local, false);
	CoverLine->AddSplinePoint(FVector(Box.Max.X, LineY, LineZ), ESplineCoordinateSpace::Local, false);
	CoverLine->SetSplinePointType(0, ESplinePointType::Linear, false);
	CoverLine->SetSplinePointType(1, ESplinePointType::Linear, true);
}


