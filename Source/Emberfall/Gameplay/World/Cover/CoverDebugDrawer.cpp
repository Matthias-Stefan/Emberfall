// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverDebugDrawer.h"

#if ENABLE_DRAW_DEBUG

#include "Emberfall/Gameplay/World/Cover/CoverGeometry.h"
#include "Emberfall/Gameplay/World/Cover/CoverObject.h"
#include "Emberfall/Gameplay/World/Cover/CoverSettings.h"
#include "Emberfall/Gameplay/World/Cover/CoverSpatialGrid.h"
#include "Emberfall/Gameplay/World/Cover/CoverTypes.h"

#include "DrawDebugHelpers.h"


FCoverDebugDrawer::FCoverDebugDrawer(const UWorld& InWorld, const UCoverSettings& InSettings)
    : World(InWorld)
    , Settings(InSettings)
{
}

void FCoverDebugDrawer::DrawCells(const FCoverSpatialGrid& Grid, float Duration) const
{
    const float CellSize = Grid.GetCellSize();
    const FVector HalfExtent(CellSize * 0.5f, CellSize * 0.5f, 0.0f);

    for (const TPair<FIntPoint, TArray<TWeakObjectPtr<ACoverObject>>>& CellEntry : Grid.GetCells())
    {
        FString Label = FString::Printf(TEXT("Cell (%d, %d): %d"),
            CellEntry.Key.X, CellEntry.Key.Y, CellEntry.Value.Num());

        for (const TWeakObjectPtr<ACoverObject>& WeakObject : CellEntry.Value)
        {
            if (const ACoverObject* CoverObject = WeakObject.Get())
            {
                Label += FString::Printf(TEXT("\n%s"), *CoverObject->GetActorNameOrLabel());
            }
        }

        const FVector CellCenter(
            (CellEntry.Key.X + 0.5f) * CellSize,
            (CellEntry.Key.Y + 0.5f) * CellSize,
            Settings.DebugGridPlaneZ);

        DrawDebugBox(&World, CellCenter, HalfExtent, FColor::Yellow, Duration < 0.0f, Duration);
        DrawDebugString(&World, CellCenter + FVector(0.0f, 0.0f, 50.0f), Label,
            nullptr, FColor::Yellow, Duration, true, 1.2f);
    }
}

void FCoverDebugDrawer::DrawGroups(const TArray<FCoverGroup>& Groups, float Duration) const
{
    for (const FCoverGroup& Group : Groups)
    {
        const FColor GroupColor = GetGroupColor(Group.GetGroupId());
        FVector GroupCenter = FVector::ZeroVector;
        int32 DrawnMembers = 0;

        for (const TWeakObjectPtr<ACoverObject>& WeakObject : Group.GetMembers())
        {
            const ACoverObject* CoverObject = WeakObject.Get();
            TArray<FVector> Corners;
            if (!CoverObject || !CoverObject->GetFootprintCorners(Corners))
            {
                continue;
            }

            FVector FootprintCenter = FVector::ZeroVector;
            for (const FVector& Corner : Corners)
            {
                FootprintCenter += Corner;
            }
            FootprintCenter /= Corners.Num();

            // Push each corner away from the center and lift it, purely so the lines are visible.
            for (FVector& Corner : Corners)
            {
                const FVector OutwardDirection = (Corner - FootprintCenter).GetSafeNormal2D();
                Corner += OutwardDirection * Settings.DebugFootprintOffsetXY;
                Corner.Z += Settings.DebugFootprintOffsetZ;
            }

            for (int32 CornerIndex = 0; CornerIndex < Corners.Num(); ++CornerIndex)
            {
                const FVector& Start = Corners[CornerIndex];
                const FVector& End = Corners[(CornerIndex + 1) % Corners.Num()];
                DrawDebugLine(&World, Start, End, GroupColor, Duration < 0.0f, Duration, 0, 4.0f);
            }

            GroupCenter += FootprintCenter;
            ++DrawnMembers;
        }

        if (DrawnMembers > 0)
        {
            GroupCenter /= DrawnMembers;
            GroupCenter.Z += Settings.DebugFootprintOffsetZ + 80.0f;
            DrawDebugString(&World, GroupCenter,
                FString::Printf(TEXT("Group %d (%d)"), Group.GetGroupId(), DrawnMembers),
                nullptr, GroupColor, Duration, true, 1.2f);
        }
    }
}

void FCoverDebugDrawer::DrawEnabledSides(const TArray<FCoverGroup>& Groups, float Duration) const
{
    const FVector Lift(0.0, 0.0, Settings.DebugFootprintOffsetZ * 2.0);

    for (const FCoverGroup& Group : Groups)
    {
        for (const TWeakObjectPtr<ACoverObject>& WeakMember : Group.GetMembers())
        {
            const ACoverObject* Member = WeakMember.Get();
            TArray<FVector> Corners;
            if (!Member || !Member->GetFootprintCorners(Corners))
            {
                continue;
            }

            FVector2D AxisX;
            FVector2D AxisY;
            Member->GetSideAxes(AxisX, AxisY);
            const ECoverSide EnabledSides = Member->GetEnabledSides();

            FVector Center = FVector::ZeroVector;
            for (const FVector& Corner : Corners)
            {
                Center += Corner;
            }
            Center /= Corners.Num();

            for (int32 CornerIndex = 0; CornerIndex < Corners.Num(); ++CornerIndex)
            {
                const FVector& Start = Corners[CornerIndex];
                const FVector& End = Corners[(CornerIndex + 1) % Corners.Num()];

                // The normal points from the center to the edge middle, so it does not depend on the winding.
                const FVector EdgeMiddle = (Start + End) * 0.5;
                const FVector2D OutwardNormal =
                    FVector2D(EdgeMiddle.X - Center.X, EdgeMiddle.Y - Center.Y).GetSafeNormal();

                const ECoverSide Side = FCoverGeometry::ClassifySide2D(OutwardNormal, AxisX, AxisY);
                const FColor SideColor = EnumHasAnyFlags(EnabledSides, Side) ? FColor::Green : FColor::Red;

                DrawDebugLine(&World, Start + Lift, End + Lift, SideColor, Duration < 0.0f, Duration, 0, 8.0f);
            }
        }
    }
}

void FCoverDebugDrawer::DrawLoops(const TArray<FCoverLoop>& Loops, float Duration) const
{
    const FVector Lift(0.0, 0.0, Settings.DebugFootprintOffsetZ);

    for (int32 LoopIndex = 0; LoopIndex < Loops.Num(); ++LoopIndex)
    {
        const FCoverLoop& Loop = Loops[LoopIndex];
        const int32 PointCount = Loop.Points.Num();
        const FColor LoopColor = GetLoopColor(LoopIndex);

        for (int32 PointIndex = 0; PointIndex < PointCount; ++PointIndex)
        {
            const FVector Start = Loop.Points[PointIndex] + Lift;
            DrawDebugString(&World, Start + FVector(0.0, 0.0, 30.0), FString::FromInt(PointIndex),
                nullptr, LoopColor, Duration, true, 1.2f);

            // An open chain has no line from its last point back to the first.
            if (PointIndex + 1 == PointCount && !Loop.bIsClosed)
            {
                continue;
            }

            const FVector End = Loop.Points[(PointIndex + 1) % PointCount] + Lift;
            DrawDebugLine(&World, Start, End, LoopColor, Duration < 0.0f, Duration, 0, 6.0f);
        }
    }
}

void FCoverDebugDrawer::DrawSides(const ACoverObject& CoverObject, float Duration) const
{
    TArray<FVector> Corners;
    if (!CoverObject.GetFootprintCorners(Corners))
    {
        return;
    }

    FVector2D AxisX;
    FVector2D AxisY;
    CoverObject.GetSideAxes(AxisX, AxisY);
    const ECoverSide EnabledSides = CoverObject.GetEnabledSides();
    const FVector Lift(0.0, 0.0, Settings.DebugFootprintOffsetZ * 2.0);

    FVector Center = FVector::ZeroVector;
    for (const FVector& Corner : Corners)
    {
        Center += Corner;
    }
    Center /= Corners.Num();

    for (int32 CornerIndex = 0; CornerIndex < Corners.Num(); ++CornerIndex)
    {
        const FVector& Start = Corners[CornerIndex];
        const FVector& End = Corners[(CornerIndex + 1) % Corners.Num()];

        // The normal points from the center to the edge middle, so it does not depend on the winding.
        const FVector EdgeMiddle = (Start + End) * 0.5;
        const FVector2D OutwardNormal = FVector2D(EdgeMiddle.X - Center.X, EdgeMiddle.Y - Center.Y).GetSafeNormal();

        const ECoverSide Side = FCoverGeometry::ClassifySide2D(OutwardNormal, AxisX, AxisY);
        const FColor SideColor = EnumHasAnyFlags(EnabledSides, Side) ? FColor::Green : FColor::Red;

        DrawDebugLine(&World, Start + Lift, End + Lift, SideColor, Duration < 0.0f, Duration, 0, 8.0f);
    }
}

FColor FCoverDebugDrawer::GetGroupColor(int32 GroupId)
{
    const uint8 Hue = static_cast<uint8>(130 + (GroupId * 37) % 70);
    const uint8 Value = static_cast<uint8>(140 + (GroupId * 83) % 115);
    return FLinearColor::MakeFromHSV8(Hue, 255, Value).ToFColor(true);
}

FColor FCoverDebugDrawer::GetLoopColor(int32 LoopIndex)
{
    // Starts in the green range so the loops stand out from the blue group footprints and the red pieces.
    const uint8 Hue = static_cast<uint8>(60 + (LoopIndex * 47) % 150);
    return FLinearColor::MakeFromHSV8(Hue, 255, 255).ToFColor(true);
}

#endif
