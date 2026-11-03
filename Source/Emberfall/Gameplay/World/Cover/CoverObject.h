// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"

#include "CoverObject.generated.h"

class USplineComponent;
class UStaticMeshComponent;


/**
 * @brief Cover actor that provides its oriented footprint and a closed spline path around it.
 */
UCLASS()
class EMBERFALL_API ACoverObject : public AActor
{
    GENERATED_BODY()

public:
    /**
     * @brief Creates the mesh root and the perimeter spline subobjects.
     */
    ACoverObject();

    /**
     * @brief Rebuilds the perimeter whenever the actor is constructed or moved in the editor.
     * @param Transform is the transform of the actor at construction time.
     */
    virtual void OnConstruction(const FTransform& Transform) override;

    /**
     * @brief Rebuilds the perimeter spline as a closed rectangle around the oriented footprint.
     * @return @c true if the spline was built, @c false if no static mesh is set.
     */
    UFUNCTION(CallInEditor, Category = "Cover")
    bool BuildPerimeter() const;

    /**
     * @brief Computes the four bottom corners of the oriented bounding box in world space.
     * @param OutCorners is filled with the corners in order, all at the bottom height of the box.
     * @param ExtentScale is the multiplier applied to the local half extents on X and Y.
     * @return @c true if the corners were computed, @c false if no static mesh is set.
     */
    bool GetFootprintCorners(TArray<FVector>& OutCorners, float ExtentScale = 1.0f) const;

protected:
    /** @brief Visible and colliding body that defines the footprint. */
    UPROPERTY(VisibleAnywhere, Category = "Cover")
    TObjectPtr<UStaticMeshComponent> CoverMesh;

    /** @brief Closed path around the footprint. */
    UPROPERTY(VisibleAnywhere, Category = "Cover")
    TObjectPtr<USplineComponent> PerimeterSpline;

    /** @brief Height of the path above the bottom of the footprint in cm. */
    UPROPERTY(EditAnywhere, Category = "Cover", meta = (ClampMin = "0.0", Units = "cm"))
    float PerimeterHeight = 0.0f;

    /** @brief Multiplier of the footprint half extents on X and Y, @c 1.0 places the path exactly on the footprint. */
    UPROPERTY(EditAnywhere, Category = "Cover", meta = (ClampMin = "1.0"))
    float PerimeterScale = 1.5f;
};