// CoverSidesComponent.cpp
// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverSidesComponent.h"

#include "Emberfall/Gameplay/World/Cover/CoverObject.h"
#include "Emberfall/Gameplay/World/Cover/CoverSettings.h"

#include "PrimitiveSceneProxy.h"
#include "SceneManagement.h"


namespace
{
    class FCoverSidesProxy final : public FPrimitiveSceneProxy
    {
    public:
        FCoverSidesProxy(const UCoverSidesComponent* Component, TArray<FVector> InLocalCorners,
            TArray<FColor> InEdgeColors, bool bInOnlySelected)
            : FPrimitiveSceneProxy(Component)
            , LocalCorners(MoveTemp(InLocalCorners))
            , EdgeColors(MoveTemp(InEdgeColors))
            , bOnlySelected(bInOnlySelected)
        {
            check(LocalCorners.Num() == EdgeColors.Num());
        }

        virtual SIZE_T GetTypeHash() const override
        {
            static size_t UniquePointer;
            return reinterpret_cast<size_t>(&UniquePointer);
        }

        virtual void GetDynamicMeshElements(const TArray<const FSceneView*>& Views, const FSceneViewFamily& ViewFamily,
            uint32 VisibilityMap, FMeshElementCollector& Collector) const override
        {
            if (bOnlySelected && !IsSelected())
            {
                return;
            }

            // The matrix is read through the accessor, the member of the base class is private.
            const FMatrix& ProxyToWorld = GetLocalToWorld();

            for (int32 ViewIndex = 0; ViewIndex < Views.Num(); ++ViewIndex)
            {
                if (!(VisibilityMap & (1 << ViewIndex)))
                {
                    continue;
                }

                FPrimitiveDrawInterface* PDI = Collector.GetPDI(ViewIndex);
                for (int32 Index = 0; Index < LocalCorners.Num(); ++Index)
                {
                    const FVector Start = ProxyToWorld.TransformPosition(LocalCorners[Index]);
                    const FVector End = ProxyToWorld.TransformPosition(LocalCorners[(Index + 1) % LocalCorners.Num()]);
                    PDI->DrawLine(Start, End, EdgeColors[Index], SDPG_Foreground, 4.0f);
                }
            }
        }

        virtual FPrimitiveViewRelevance GetViewRelevance(const FSceneView* View) const override
        {
            FPrimitiveViewRelevance Relevance;
            Relevance.bDrawRelevance = IsShown(View);
            Relevance.bDynamicRelevance = true;
            return Relevance;
        }

        virtual uint32 GetMemoryFootprint() const override { return sizeof(*this) + GetAllocatedSize(); }

    private:
        TArray<FVector> LocalCorners;
        TArray<FColor> EdgeColors;
        bool bOnlySelected = false;
    };
}


UCoverSidesComponent::UCoverSidesComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    bHiddenInGame = true;
    UPrimitiveComponent::SetCollisionEnabled(ECollisionEnabled::NoCollision);
}

FPrimitiveSceneProxy* UCoverSidesComponent::CreateSceneProxy()
{
    const UCoverSettings* Settings = GetDefault<UCoverSettings>();
    const ACoverObject* CoverObject = Cast<ACoverObject>(GetOwner());
    if (!CoverObject || !Settings->bDrawSidesInEditor)
    {
        return nullptr;
    }

    TArray<FVector> WorldCorners;
    TArray<bool> EdgeEnabled;
    if (!CoverObject->GetFootprintEdges(WorldCorners, EdgeEnabled))
    {
        return nullptr;
    }

    // The proxy draws in local space, so a moved wall needs no new proxy.
    const FTransform ComponentTransform = GetComponentTransform();
    const FVector Lift(0.0, 0.0, Settings->DebugFootprintOffsetZ);

    TArray<FVector> LocalCorners;
    TArray<FColor> EdgeColors;
    for (int32 Index = 0; Index < WorldCorners.Num(); ++Index)
    {
        LocalCorners.Add(ComponentTransform.InverseTransformPosition(WorldCorners[Index] + Lift));
        EdgeColors.Add(EdgeEnabled[Index] ? FColor::Green : FColor::Red);
    }

    return new FCoverSidesProxy(this, MoveTemp(LocalCorners), MoveTemp(EdgeColors), Settings->bDrawSidesOnlySelected);
}

FBoxSphereBounds UCoverSidesComponent::CalcBounds(const FTransform& LocalToWorld) const
{
    // The sides lie on the footprint, so the bounds of the parent mesh with a margin cover them.
    if (const USceneComponent* Parent = GetAttachParent())
    {
        return Parent->Bounds.ExpandBy(100.0);
    }
    return FBoxSphereBounds(LocalToWorld.GetLocation(), FVector(200.0), 200.0);
}