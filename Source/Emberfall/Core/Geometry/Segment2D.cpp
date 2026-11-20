// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Core/Geometry/Segment2D.h"

#include <limits>


const FSegment2D FSegment2D::Invalid(
    FVector2D(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
    FVector2D(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()));

bool FSegment2D::IntersectLine(const FSegment2D& Other, double& OutAlpha, double& OutOtherAlpha) const
{
    const FVector2D Direction = GetDirection();
    const FVector2D OtherDirection = Other.GetDirection();
    const double Denominator = FVector2D::CrossProduct(Direction, OtherDirection);
    if (FMath::IsNearlyZero(Denominator))
    {
        return false;
    }

    const FVector2D StartToOtherStart = Other.GetStart() - Start;
    OutAlpha = FVector2D::CrossProduct(StartToOtherStart, OtherDirection) / Denominator;
    OutOtherAlpha = FVector2D::CrossProduct(StartToOtherStart, Direction) / Denominator;
    return true;
}

bool FSegment2D::IntersectSegment(const FSegment2D& Other, double& OutAlpha) const
{
    double Alpha = 0.0;
    double OtherAlpha = 0.0;
    if (!IntersectLine(Other, Alpha, OtherAlpha))
    {
        return false;
    }

    // The lines meet, but the point must also lie on both real segments. The little slack makes segments that
    // touch at an end point count, without it floating point noise misses such T junctions at random.
    const double Slack = UE_KINDA_SMALL_NUMBER;
    const bool bHitsThis = Alpha >= -Slack && Alpha <= 1.0 + Slack;
    const bool bHitsOther = OtherAlpha >= -Slack && OtherAlpha <= 1.0 + Slack;
    if (!bHitsThis || !bHitsOther)
    {
        return false;
    }

    OutAlpha = FMath::Clamp(Alpha, 0.0, 1.0);
    return true;
}

TArray<FSegment2D> FSegment2D::SplitAtAlphas(const TArray<double>& Alphas) const
{
    // Work on a copy, so the caller's list stays untouched.
    TArray<double> SortedAlphas;
    SortedAlphas.Reserve(Alphas.Num() + 2);
    for (const double Alpha : Alphas)
    {
        SortedAlphas.Add(FMath::Clamp(Alpha, 0.0, 1.0));
    }
    SortedAlphas.Sort();

    // The borders turn n split positions into n + 1 pieces.
    SortedAlphas.Insert(0.0, 0);
    SortedAlphas.Add(1.0);

    TArray<FSegment2D> Pieces;
    Pieces.Reserve(SortedAlphas.Num() - 1);
    for (int32 Index = 0; Index < SortedAlphas.Num() - 1; ++Index)
    {
        const double StartAlpha = SortedAlphas[Index];
        const double EndAlpha = SortedAlphas[Index + 1];

        // A split at an end point or two splits at the same spot would yield a piece without length.
        if (FMath::IsNearlyEqual(StartAlpha, EndAlpha, UE_KINDA_SMALL_NUMBER))
        {
            continue;
        }

        Pieces.Emplace(GetPointAt(StartAlpha), GetPointAt(EndAlpha));
    }

    return Pieces;
}
