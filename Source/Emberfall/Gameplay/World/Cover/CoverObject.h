// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "Emberfall/Gameplay/World/Cover/CoverTypes.h"

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"

#include "CoverObject.generated.h"

class ACoverObject;
class USplineComponent;
class UStaticMeshComponent;


/** @brief Event fired with the object as argument when its transform changed. */
DECLARE_MULTICAST_DELEGATE_OneParam(FOnCoverObjectChanged, ACoverObject*);

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
     * @brief Computes the four bottom corners of the oriented bounding box in world space.
     * @param OutCorners is filled with the corners in order, all at the bottom height of the box.
     * @param ExtentScale is the multiplier applied to the local half extents on X and Y.
     * @return @c true if the corners were computed, @c false if no static mesh is set.
     */
    bool GetFootprintCorners(TArray<FVector>& OutCorners, float ExtentScale = 1.0f) const;

    /**
     * @brief Gets the sides that take part in the cover path.
     * @return Enabled sides as flags in local space, bits outside of @c ECoverSide are masked out.
     */
    ECoverSide GetEnabledSides() const;

    /**
     * @brief Computes the world directions of the local positive X and Y axes in the ground plane.
     * @param OutAxisX is filled with the direction of the local positive X axis, normalized.
     * @param OutAxisY is filled with the direction of the local positive Y axis, normalized.
     */
    void GetSideAxes(FVector2D& OutAxisX, FVector2D& OutAxisY) const;
    
    /**
     * @brief Subscribes a listener to transform changes of this object.
     * @param Listener is the object that receives the call.
     * @param Function is the member function to call with this object as argument.
     */
    template <typename UserClass>
    void AddChangedListener(UserClass* Listener, void (UserClass::*Function)(ACoverObject*))
    {
        OnChanged.AddUObject(Listener, Function);
    }

    /**
     * @brief Removes every subscription of a listener.
     * @param Listener is the object whose subscriptions are removed.
     */
    void RemoveChangedListeners(const void* Listener)
    {
        OnChanged.RemoveAll(Listener);
    }

    /**
     * @brief Rebuilds the perimeter spline as a closed rectangle around the oriented footprint.
     * @return @c true if the spline was built, @c false if no static mesh is set.
     */
    UFUNCTION(CallInEditor, Category = "Cover")
    bool BuildPerimeter() const;

protected:
    /**
     * @brief Registers the object at the cover subsystem of its world.
     */
    virtual void BeginPlay() override;

    /**
     * @brief Unregisters the object at the cover subsystem of its world.
     * @param EndPlayReason is the reason the actor stops playing.
     */
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

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

    /** @brief Sides that take part in the cover path as @c ECoverSide flags in local space, all four by default. */
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Cover",
        meta = (Bitmask, BitmaskEnum = "/Script/Emberfall.ECoverSide"))
    int32 EnabledSides = static_cast<int32>(ECoverSide::All);
    
private:
    /**
     * @brief Forwards a transform change of the cover mesh as a change event of this object.
     * @param UpdatedComponent is the component whose transform changed, not used.
     * @param UpdateTransformFlags is the way the transform was updated, not used.
     * @param Teleport is the kind of move that caused the update, not used.
     */
    void HandleMeshTransformUpdated(USceneComponent* UpdatedComponent, EUpdateTransformFlags UpdateTransformFlags,
        ETeleportType Teleport);
    
    /** @brief Event fired with this object as argument when its transform changed, only this class broadcasts it. */
    FOnCoverObjectChanged OnChanged;
    
    /** @brief Subscription to the transform updates of the cover mesh, valid between @c BeginPlay and @c EndPlay. */
    FDelegateHandle TransformUpdatedHandle;
};