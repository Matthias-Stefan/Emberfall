#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CoverObject.generated.h"

class USplineComponent;


/**
 * @brief Cover actor that provides a closed spline path around its bounds.
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
     * @param Transform The actor's transform at construction time.
     */
    virtual void OnConstruction(const FTransform& Transform) override;
    
    /**
     * @brief Rebuilds @c PerimeterSpline as a closed rectangle around the actor's bounds.
     * @return @c true if the spline was built, @c false if the bounds are empty.
     */
    UFUNCTION(CallInEditor, Category = "Cover")
    bool BuildPerimeter();

    /**
     * @brief Computes the four bottom corners of the oriented bounding box in world space.
     * @param OutCorners Receives the corners in order, all at the bottom height of the box.
     * @param ExtentScale Multiplier applied to the local half extents on X and Y.
     * @return @c true if the corners were computed, @c false if no static mesh is set.
     */
    bool GetFootprintCorners(TArray<FVector>& OutCorners, float ExtentScale = 1.0f) const;
    
protected:
    /** @brief Visible and colliding body of the cover; defines the bounds for the perimeter. */
    UPROPERTY(VisibleAnywhere, Category = "Cover")
    TObjectPtr<UStaticMeshComponent> CoverMesh;
    
    /** @brief Closed path around the cover object. */
    UPROPERTY(VisibleAnywhere, Category = "Cover")
    TObjectPtr<USplineComponent> PerimeterSpline;

    /** @brief Height of the path above the bounds' bottom in cm. */
    UPROPERTY(EditAnywhere, Category = "Cover", meta = (ClampMin = "0.0"))
    float PerimeterHeight = 0.0f;
    
    /** @brief Multiplier applied to the bounds' half extents on X and Y (@c 1.0 = exactly on the bounds). */
    UPROPERTY(EditAnywhere, Category = "Cover", meta = (ClampMin = "1.0"))
    float PerimeterScale = 1.5f;
};