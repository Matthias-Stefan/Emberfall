// CoverSettings.h
#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "CoverSettings.generated.h"


/**
 * @brief Project-wide tuning values for the cover system.
 */
UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "Cover"))
class EMBERFALL_API UCoverSettings : public UDeveloperSettings
{
    GENERATED_BODY()

public:
    UCoverSettings();

    /** @brief Edge length of one spatial grid cell in cm. */
    UPROPERTY(Config, EditAnywhere, Category = "Grid", meta = (ClampMin = "100.0", Units = "cm"))
    float CellSize = 1000.0f;

    /** @brief Distance in cm below which two footprints count as touching. */
    UPROPERTY(Config, EditAnywhere, Category = "Grid", meta = (ClampMin = "0.0", Units = "cm"))
    float MergeRadius = 50.0f;

//~=============================================================================
// Debug
    
    /** @brief If @c true, the occupied grid cells are drawn when the world begins play. */
    UPROPERTY(Config, EditAnywhere, Category = "Debug")
    bool bDrawDebugGrid = false;
    
    /** @brief World Z in cm at which the debug grid cells and labels are drawn. */
    UPROPERTY(Config, EditAnywhere, Category = "Debug", meta = (Units = "cm"))
    float DebugGridPlaneZ = 0.0f;
    
    /** @brief Distance in cm the debug footprints are pushed outward, purely visual. */
    UPROPERTY(Config, EditAnywhere, Category = "Debug", meta = (ClampMin = "0.0", Units = "cm"))
    float DebugFootprintOffsetXY = 10.0f;

    /** @brief Height in cm the debug footprints are lifted above the footprint, purely visual. */
    UPROPERTY(Config, EditAnywhere, Category = "Debug", meta = (ClampMin = "0.0", Units = "cm"))
    float DebugFootprintOffsetZ = 15.0f;
};