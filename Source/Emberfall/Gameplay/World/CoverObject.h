// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CoverObject.generated.h"

class USplineComponent;


/** Trace channel "Cover", must match Project Settings. */
#define ECC_COVER ECC_GameTraceChannel1

/** @brief Height class of a cover object. */
UENUM(BlueprintType)
enum class ECoverHeight : uint8
{
	/** @brief Crouch behind it. */
	Low,

	/** @brief Stand and lean against it. */
	High
};

/**
 * @brief Anything a unit can take cover behind or lean against.
 */
UCLASS()
class EMBERFALL_API ACoverObject : public AActor
{
	GENERATED_BODY()

public:
	ACoverObject();

	/**
	 * @brief Refits the cover line to the mesh bounds when @c bAutoFitLine is set.
	 * @param Transform Actor transform used for construction.
	 */
	virtual void OnConstruction(const FTransform& Transform) override;
	
	/**
	 * @brief Returns the cover line spline.
	 * @return Spline running along the cover face the units dock to.
	 */
	USplineComponent* GetCoverLine() const { return CoverLine; }
	
	/**
	 * @brief Returns the height class of this cover.
	 * @return @c ECoverHeight of the object.
	 */
	ECoverHeight GetCoverHeight() const { return CoverHeight; }
	
	/**
	 * @brief Returns the outward normal of the face the cover line sits on.
	 * @return World-space unit vector pointing away from the docking face.
	 */
	FVector GetDockNormal() const { return Mesh->GetRightVector(); };

	/**
	 * @brief Checks whether a unit hitting the cover at the given surface may dock.
	 * @param SurfaceNormal Normal of the surface hit by the cover trace.
	 * @return @c true if the normal points to the docking side of the cover.
	 */
	bool CanDockFromNormal(const FVector& SurfaceNormal) const;
	
private:
	/** @brief Places the two @c CoverLine points along the X axis of the mesh bounds. */
    void FitCoverLineToMesh();
	
protected:
	/** @brief Visual mesh of the cover object, blocks the @c Cover trace channel. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Cover", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<UStaticMeshComponent> Mesh;

	/** @brief Height class of the cover, decides crouch vs. stand animation. */
	UPROPERTY(EditAnywhere, Category = "Cover")
	ECoverHeight CoverHeight = ECoverHeight::Low;
	
	
	/** @brief Line along the cover face, units move on it while in cover. */
	UPROPERTY(EditAnywhere, Category = "Cover")
	TObjectPtr<USplineComponent> CoverLine;
	
	/** @brief When @c true the cover line is rebuilt from the mesh bounds on every construction, overwriting manual edits. */
	UPROPERTY(EditAnywhere, Category = "Cover")
	bool bAutoFitLine = true;
	
	/** @brief Distance in cm (world units) the cover line is moved outwards from the +Y face of the mesh. */
	UPROPERTY(EditAnywhere, Category = "Cover")
	float LineOffset = 30.0f;
};
