// CoverSettings.h
// Copyright (c) 2026 Emberfall. All Rights Reserved.

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
    /**
     * @brief Places the settings under the Emberfall category of the project settings.
     */
    UCoverSettings();

    //~=============================================================================
    // Grid

    /** @brief Edge length of one spatial grid cell in cm. */
    UPROPERTY(Config, EditAnywhere, Category = "Grid", meta = (ClampMin = "100.0", Units = "cm"))
    float CellSize = 1000.0f;

    /** @brief Distance below which two footprints count as touching in cm. */
    UPROPERTY(Config, EditAnywhere, Category = "Grid", meta = (ClampMin = "0.0", Units = "cm"))
    float MergeRadius = 50.0f;

    //~=============================================================================
    // Outline

    /** @brief Distance the outline keeps from the footprints in cm, at least half of @c MergeRadius so groups do not split. */
    UPROPERTY(Config, EditAnywhere, Category = "Outline", meta = (ClampMin = "0.0", Units = "cm"))
    float OutlineOffset = 80.0f;

    /** @brief Distance to an edge below which a point counts as on the border of a footprint in cm. */
    UPROPERTY(Config, EditAnywhere, Category = "Outline", meta = (ClampMin = "0.0", Units = "cm"))
    float OutlineBorderTolerance = 0.1f;

    /** @brief Largest distance from the simplified line at which outline points are dropped in cm. */
    UPROPERTY(Config, EditAnywhere, Category = "Outline", meta = (ClampMin = "0.0", Units = "cm"))
    float OutlineSimplifyTolerance = 15.0f;

    /** @brief Smallest area an outline loop needs to be kept in cm², smaller loops count as gaps from imprecise placement. */
    UPROPERTY(Config, EditAnywhere, Category = "Outline", meta = (ClampMin = "0.0"))
    float OutlineMinLoopArea = 10000.0f;
    
    /** @brief Smallest length an open outline chain needs to be kept in cm, shorter chains count as leftovers. */
    UPROPERTY(Config, EditAnywhere, Category = "Outline", meta = (ClampMin = "0.0", Units = "cm"))
    float OutlineMinChainLength = 50.0f;
    
    //~=============================================================================
    // Debug

    /** @brief Whether the grid cells, groups, enabled sides and outline loops are drawn when the world begins play. */
    UPROPERTY(Config, EditAnywhere, Category = "Debug")
    bool bDrawDebugGrid = false;

    /** @brief Whether the enabled and disabled sides of every wall are drawn in the editor viewport without playing. */
    UPROPERTY(Config, EditAnywhere, Category = "Debug")
    bool bDrawSidesInEditor = false;

    /** @brief Whether the editor side drawing is limited to the selected walls, otherwise all walls are drawn. */
    UPROPERTY(Config, EditAnywhere, Category = "Debug", meta = (EditCondition = "bDrawSidesInEditor"))
    bool bDrawSidesOnlySelected = true;

#if WITH_EDITOR
    /**
     * @brief Rebuilds the editor side drawing of all cover objects when one of the drawing settings changed.
     * @param PropertyChangedEvent is the description of the property that changed.
     */
    virtual void PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent) override;
#endif
    
    /** @brief World Z of the plane on which the debug grid cells and labels are drawn in cm. */
    UPROPERTY(Config, EditAnywhere, Category = "Debug", meta = (Units = "cm"))
    float DebugGridPlaneZ = 0.0f;

    /** @brief Horizontal offset applied to the debug footprints in cm, positive moves them outward. */
    UPROPERTY(Config, EditAnywhere, Category = "Debug", meta = (ClampMin = "0.0", Units = "cm"))
    float DebugFootprintOffsetXY = 10.0f;

    /** @brief Vertical offset applied to the debug footprints in cm, positive moves them up. */
    UPROPERTY(Config, EditAnywhere, Category = "Debug", meta = (ClampMin = "0.0", Units = "cm"))
    float DebugFootprintOffsetZ = 15.0f;
};