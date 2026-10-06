// Copyright (c) 2026 Emberfall. All Rights Reserved.


#include "SelectionDragState.h"

void FSelectionDragState::Begin(FVector2D StartPos)
{
	DragStart = StartPos;
	bPressed = true;
	bIsDragging = false;
}

void FSelectionDragState::Update(FVector2D Current, float Threshold)
{
	if (!bPressed || bIsDragging)
	{
		return;
	}
	
	if (FVector2D::Distance(DragStart, Current) > Threshold)
	{
		bIsDragging = true;
	}
}

bool FSelectionDragState::Complete()
{
	const bool bWasDragging = bIsDragging;
	Reset();
	return bWasDragging;
}

void FSelectionDragState::Reset()
{
	DragStart = FVector2D::ZeroVector;
	bPressed = false;
	bIsDragging = false;
}
