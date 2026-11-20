// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include <limits>

#include "Emberfall/Core/Geometry/Segment2D.h"


const FSegment2D FSegment2D::Invalid(
    FVector2D(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
    FVector2D(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()));

bool FSegment2D::IntersectLines(const FSegment2D& Other, FVector2D& OutPoint) const
{
    const FVector2D Direction = GetDirection();
    const FVector2D OtherDirection = Other.GetDirection();
    const double Denominator = FVector2D::CrossProduct(Direction, OtherDirection);
    if (FMath::IsNearlyZero(Denominator))
    {
        return false;
    }

    const FVector2D StartToOtherStart = Other.GetStart() - Start;
    const double Alpha = FVector2D::CrossProduct(StartToOtherStart, OtherDirection) / Denominator;
    OutPoint = GetPointAt(Alpha);
    return true;
}
