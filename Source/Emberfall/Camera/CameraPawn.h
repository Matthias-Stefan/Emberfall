// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"

#include "CameraPawn.generated.h"


class UCameraComponent;
class UInputAction;
class UInputMappingContext;
class USpringArmComponent;
struct FInputActionValue;

/**
 * @brief Free-flying top-down camera the player uses to look around the level.
 */
UCLASS()
class EMBERFALL_API ACameraPawn : public APawn
{
	GENERATED_BODY()

public:
	/** @brief Default constructor. */
	ACameraPawn();
	
	/**
	 * @brief Binds the pan and zoom actions.
	 * @param PlayerInputComponent The input component of the possessing controller.
	 */
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

	/**
	 * @brief Moves the camera on the ground plane relative to its yaw.
	 * @param Input X = sideways (A/D), Y = forward (W/S), expected within -1..1.
	 */
	void AddPanInput(const FVector2D& Input);
	
protected:
	/** @brief Applies the editable arm length and pitch to the spring arm. */
	virtual void BeginPlay() override;
	
	/** @brief Registers the mapping context once the pawn is possessed by a local player. */
	virtual void PawnClientRestart() override;
	
	/**
	 * @brief Moves the camera on the ground plane.
	 * @param Value Pan input as @c FVector2D (X = right, Y = forward).
	 */
	void Pan(const FInputActionValue& Value);
	
	/**
	 * @brief Changes the arm length, clamped to the zoom limits.
	 * @param Value Zoom input as @c float (mouse wheel axis).
	 */
	void Zoom(const FInputActionValue& Value);

	/** @brief Starts the rotate mode (middle mouse button pressed). */
	void OnRotateModeStarted();

	/** @brief Ends the rotate mode (middle mouse button released). */
	void OnRotateModeCompleted();

	/**
	 * @brief Rotates the camera around the vertical axis while the rotate mode is active.
	 * @param Value Horizontal mouse movement as @c float.
	 */
	void Look(const FInputActionValue& Value);
	
protected:
	/** @brief Distance between the camera and the pawn. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera", meta = (ClampMin = "100", Units = "cm"))
	float ArmLength{ 1500.0f };

	/** @brief Downward tilt of the camera; -90 looks straight down. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera", meta = (ClampMin = "-89", ClampMax = "-10", Units = "Degrees"))
	float Pitch{ -55.0f };
	
	/** @brief Current yaw of the camera in degrees; starts at this value and is updated while rotating. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera", meta = (Units = "Degrees"))
	float Yaw{ 31.0f };

	/** @brief Pan speed on the ground plane. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera|Pan", meta = (ClampMin = "0", Units = "cm/s"))
	float PanSpeed{ 2000.0f };

	/** @brief Closest zoom distance. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera|Zoom", meta = (ClampMin = "100", Units = "cm"))
	float MinArmLength{ 500.0f };

	/** @brief Farthest zoom distance. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera|Zoom", meta = (ClampMin = "100", Units = "cm"))
	float MaxArmLength{ 3000.0f };

	/** @brief Arm length change per mouse wheel tick. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera|Zoom", meta = (ClampMin = "0", Units = "cm"))
	float ZoomStep{ 150.0f };

	/** @brief Mapping context with the camera keys (IMC_Camera). */
	UPROPERTY(EditAnywhere, Category = "Input")
	TObjectPtr<UInputMappingContext> MappingContext{ nullptr };

	/** @brief Pan action (Axis2D, IA_Pan). */
	UPROPERTY(EditAnywhere, Category = "Input")
	TObjectPtr<UInputAction> PanAction{ nullptr };

	/** @brief Zoom action (Axis1D, IA_Zoom). */
	UPROPERTY(EditAnywhere, Category = "Input")
	TObjectPtr<UInputAction> ZoomAction{ nullptr };
	
	/** @brief Rotate mode action (Digital, IA_RotateMode); active while the middle mouse button is held. */
	UPROPERTY(EditAnywhere, Category = "Input")
	TObjectPtr<UInputAction> RotateModeAction{ nullptr };

	/** @brief Look action (Axis1D, IA_Look); horizontal mouse movement used for rotating. */
	UPROPERTY(EditAnywhere, Category = "Input")
	TObjectPtr<UInputAction> LookAction{ nullptr };
	
	/** @brief Rotation in degrees per mouse movement unit. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Camera|Rotate", meta = (ClampMin = "0"))
	float RotateSensitivity{ 0.3f };
	
private:
	/** @brief Root scene component; the pan movement moves this. */
	UPROPERTY()
	TObjectPtr<USceneComponent> Root{ nullptr };

	/** @brief Arm that holds the camera at a fixed pitch above the ground. */
	UPROPERTY()
	TObjectPtr<USpringArmComponent> SpringArm{ nullptr };

	/** @brief The gameplay camera. */
	UPROPERTY()
	TObjectPtr<UCameraComponent> Camera{ nullptr };
	
	/** @brief True while the middle mouse button is held. */
	bool bRotating{ false };
};