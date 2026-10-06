// Copyright (c) 2026 Emberfall. All Rights Reserved.


#include "SelectionSettings.h"

USelectionSettings::USelectionSettings()
{
	CategoryName = TEXT("Emberfall");

	HoverColor = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("4FE3E0")));
	SelectColor = FLinearColor::FromSRGBColor(FColor::FromHex(TEXT("FF3EA5")));
}

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