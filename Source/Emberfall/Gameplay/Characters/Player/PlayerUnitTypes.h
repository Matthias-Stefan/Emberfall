// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"


//~=============================================================================
// Player Unit Types

/** @brief Visual selection state of a unit. */
UENUM(BlueprintType)
enum class EPlayerUnitTypes : uint8
{
	None,
	Hovered,
	Selected
};
