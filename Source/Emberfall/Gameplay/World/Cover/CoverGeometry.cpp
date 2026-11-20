// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverGeometry.h"

#include "Algo/Reverse.h"


FPolygon2D FCoverGeometry::ToPolygon2D(const TArray<FVector>& Corners)
{
    TArray<FVector2D> Points;
    Points.Reserve(Corners.Num());
    for (const FVector& Corner : Corners)
    {
        Points.Emplace(Corner.X, Corner.Y);
    }

    return FPolygon2D(MoveTemp(Points));
}

FPolyline2D FCoverGeometry::ToPolyline2D(const TArray<FVector>& Points, bool bIsClosed)
{
    TArray<FVector2D> FlatPoints;
    FlatPoints.Reserve(Points.Num());
    for (const FVector& Point : Points)
    {
        FlatPoints.Emplace(Point.X, Point.Y);
    }

    return FPolyline2D(MoveTemp(FlatPoints), bIsClosed);
}

bool FCoverGeometry::BuildGrownCorners(const TArray<FVector>& ConvexCorners, double Offset, double MiterLimit,
    TArray<FVector>& OutCorners)
{
    OutCorners.Reset();

    // The polygon offset keeps the winding, but the outline code relies on the right-hand edge normal
    // pointing outward, which holds for counterclockwise corners only. Mirrored footprints get reversed.
    TArray<FVector> OrderedCorners = ConvexCorners;
    if (ToPolygon2D(ConvexCorners).GetSignedArea() < 0.0)
    {
        Algo::Reverse(OrderedCorners);
    }

    const FPolygon2D GrownPolygon = ToPolygon2D(OrderedCorners).BuildOffset(Offset, MiterLimit);
    if (!GrownPolygon.IsValid())
    {
        return false;
    }

    // The polygon has no height, every grown corner takes the one of the corner it was grown from.
    OutCorners.Reserve(GrownPolygon.GetPointNum());
    for (int32 CornerIndex = 0; CornerIndex < GrownPolygon.GetPointNum(); ++CornerIndex)
    {
        const FVector2D& GrownPoint = GrownPolygon.GetPoint(CornerIndex);
        OutCorners.Emplace(GrownPoint.X, GrownPoint.Y, OrderedCorners[CornerIndex].Z);
    }
    return true;
}

ECoverSide FCoverGeometry::ClassifySide2D(const FVector2D& OutwardNormal, const FVector2D& AxisX,
    const FVector2D& AxisY)
{
    // Projection of the normal on each local axis: positive means it faces along the axis, negative against it.
    const double AlongX = FVector2D::DotProduct(OutwardNormal, AxisX);
    const double AlongY = FVector2D::DotProduct(OutwardNormal, AxisY);

    // The axis with the larger projection wins, its sign picks the side. Pieces run parallel to the wall edges,
    // so a tie between the two axes does not occur.
    if (FMath::Abs(AlongX) >= FMath::Abs(AlongY))
    {
        return AlongX >= 0.0 ? ECoverSide::PositiveX : ECoverSide::NegativeX;
    }
    return AlongY >= 0.0 ? ECoverSide::PositiveY : ECoverSide::NegativeY;
}
