// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Settings/SelectionSettings.h"

#include "Materials/MaterialParameterCollection.h"


USelectionSettings::USelectionSettings()
{
	CategoryName = TEXT("Emberfall");

	HoverColor = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("85E3B7")));
	SelectColor = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("FF3EA5")));
}

#if WITH_EDITOR
void USelectionSettings::PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent)
{
	Super::PostEditChangeProperty(PropertyChangedEvent);

	UMaterialParameterCollection* Collection = OutlineParameters.LoadSynchronous();
	if (Collection == nullptr)
	{
		return;
	}

	// Write the settings into the asset defaults; parameters are matched by name
	for (FCollectionVectorParameter& Parameter : Collection->VectorParameters)
	{
		if (Parameter.ParameterName == FName(TEXT("HoverColor")))
		{
			Parameter.DefaultValue = HoverColor;
		}
		else if (Parameter.ParameterName == FName(TEXT("SelectColor")))
		{
			Parameter.DefaultValue = SelectColor;
		}
	}

	// Dirty so the asset can be saved, PostEditChange so materials pick up the new defaults
	Collection->MarkPackageDirty();
	Collection->PostEditChange();
}
#endif

FLinearColor USelectionSettings::GetBoxFillColor() const
{
	FLinearColor Color = HoverColor;
	Color.A = BoxFillAlpha;
	return Color;
}

FLinearColor USelectionSettings::GetBoxBorderColor() const
{
	FLinearColor Color = HoverColor;
	Color.A = BoxBorderAlpha;
	return Color;
}