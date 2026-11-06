// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/PrimitiveComponent.h"

#include "CoverSidesComponent.generated.h"


/**
 * @brief Editor-only visualization of the enabled and disabled sides of a cover object.
 */
UCLASS(ClassGroup = (Emberfall), HideCategories = (Collision, Physics, Rendering, Navigation, Cooking))
class EMBERFALL_API UCoverSidesComponent : public UPrimitiveComponent
{
    GENERATED_BODY()

public:
    /**
     * @brief Creates the component hidden in game and without collision.
     */
    UCoverSidesComponent();

    /**
     * @brief Creates the proxy that draws the footprint edges in green for enabled sides and red for disabled sides.
     * @return The proxy, @c nullptr if the owner is no cover object, the drawing is switched off or no footprint exists.
     */
    virtual FPrimitiveSceneProxy* CreateSceneProxy() override;

    /**
     * @brief Computes the bounds of the drawing from the bounds of the parent mesh.
     * @param LocalToWorld is the transform of the component to world space.
     * @return Bounds that cover the footprint edges.
     */
    virtual FBoxSphereBounds CalcBounds(const FTransform& LocalToWorld) const override;
};