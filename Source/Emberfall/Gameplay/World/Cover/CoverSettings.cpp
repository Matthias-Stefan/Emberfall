// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverSettings.h"

#if WITH_EDITOR
#include "Emberfall/Gameplay/World/Cover/CoverSidesComponent.h"

#include "UObject/UObjectIterator.h"
#endif


UCoverSettings::UCoverSettings()
{
    CategoryName = TEXT("Emberfall");
}

#if WITH_EDITOR
void UCoverSettings::PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent)
{
    Super::PostEditChangeProperty(PropertyChangedEvent);

    const FName PropertyName = PropertyChangedEvent.GetPropertyName();
    const bool bAffectsSideDrawing =
        PropertyName == GET_MEMBER_NAME_CHECKED(UCoverSettings, bDrawSidesInEditor)
        || PropertyName == GET_MEMBER_NAME_CHECKED(UCoverSettings, bDrawSidesOnlySelected)
        || PropertyName == GET_MEMBER_NAME_CHECKED(UCoverSettings, DebugFootprintOffsetZ);
    if (!bAffectsSideDrawing)
    {
        return;
    }

    // The proxies copy the settings when they are created, so every visualizer has to build its proxy again.
    for (TObjectIterator<UCoverSidesComponent> It; It; ++It)
    {
        if (!It->IsTemplate())
        {
            It->MarkRenderStateDirty();
        }
    }
}
#endif