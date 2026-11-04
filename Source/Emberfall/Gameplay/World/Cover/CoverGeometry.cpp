// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverGeometry.h"


bool FCoverGeometry::ContainsPoint2D(const TArray<FVector>& QuadCorners, const FVector& Point)
{
    if (QuadCorners.Num() < 3)
    {
        return false;
    }

    bool bHasPositiveSide = false;
    bool bHasNegativeSide = false;

    for (int32 CornerIndex = 0; CornerIndex < QuadCorners.Num(); ++CornerIndex)
    {
        const FVector& Current = QuadCorners[CornerIndex];
        const FVector& Next = QuadCorners[(CornerIndex + 1) % QuadCorners.Num()];

        const double Cross = (Next.X - Current.X) * (Point.Y - Current.Y)
                           - (Next.Y - Current.Y) * (Point.X - Current.X);
        bHasPositiveSide |= Cross > 0.0;
        bHasNegativeSide |= Cross < 0.0;
    }

    // A point on an edge has Cross == 0 there and sets neither flag, so the border counts as inside.
    return !(bHasPositiveSide && bHasNegativeSide);
}

bool FCoverGeometry::ContainsPointStrict2D(const TArray<FVector>& QuadCorners, const FVector& Point,
                                           double BorderTolerance)
{
    if (QuadCorners.Num() < 3)
    {
        return false;
    }

    // Sign of the first edge decides which side counts as inside, so either winding works.
    double InsideSign = 0.0;

    for (int32 CornerIndex = 0; CornerIndex < QuadCorners.Num(); ++CornerIndex)
    {
        const FVector& Current = QuadCorners[CornerIndex];
        const FVector& Next = QuadCorners[(CornerIndex + 1) % QuadCorners.Num()];

        const FVector2D EdgeDirection(Next.X - Current.X, Next.Y - Current.Y);
        const double EdgeLength = EdgeDirection.Size();

        // A degenerate edge has no side, so the test cannot give a meaningful answer.
        if (EdgeLength < UE_KINDA_SMALL_NUMBER)
        {
            return false;
        }

        // Cross product divided by the edge length is the signed distance of the point to the edge in cm.
        const double SignedDistance = (EdgeDirection.X * (Point.Y - Current.Y)
                                     - EdgeDirection.Y * (Point.X - Current.X)) / EdgeLength;

        if (FMath::Abs(SignedDistance) <= BorderTolerance)
        {
            return false;
        }

        const double EdgeSign = SignedDistance > 0.0 ? 1.0 : -1.0;
        if (InsideSign == 0.0)
        {
            InsideSign = EdgeSign;
        }
        else if (EdgeSign != InsideSign)
        {
            return false;
        }
    }
    return true;
}

double FCoverGeometry::DistanceSquared2D(const TArray<FVector>& FirstQuadCorners,
                                         const TArray<FVector>& SecondQuadCorners)
{
    if (FirstQuadCorners.IsEmpty() || SecondQuadCorners.IsEmpty())
    {
        return TNumericLimits<double>::Max();
    }

    // Catches the case where one quad lies completely inside the other.
    if (ContainsPoint2D(SecondQuadCorners, FirstQuadCorners[0]) ||
        ContainsPoint2D(FirstQuadCorners, SecondQuadCorners[0]))
    {
        return 0.0;
    }

    double BestDistanceSquared = TNumericLimits<double>::Max();
    for (int32 FirstIndex = 0; FirstIndex < FirstQuadCorners.Num(); ++FirstIndex)
    {
        const FVector& FirstCurrent = FirstQuadCorners[FirstIndex];
        const FVector& FirstNext = FirstQuadCorners[(FirstIndex + 1) % FirstQuadCorners.Num()];
        const FVector FirstStart(FirstCurrent.X, FirstCurrent.Y, 0.0);
        const FVector FirstEnd(FirstNext.X, FirstNext.Y, 0.0);

        for (int32 SecondIndex = 0; SecondIndex < SecondQuadCorners.Num(); ++SecondIndex)
        {
            const FVector& SecondCurrent = SecondQuadCorners[SecondIndex];
            const FVector& SecondNext = SecondQuadCorners[(SecondIndex + 1) % SecondQuadCorners.Num()];
            const FVector SecondStart(SecondCurrent.X, SecondCurrent.Y, 0.0);
            const FVector SecondEnd(SecondNext.X, SecondNext.Y, 0.0);

            FVector ClosestOnFirst;
            FVector ClosestOnSecond;
            FMath::SegmentDistToSegmentSafe(FirstStart, FirstEnd, SecondStart, SecondEnd, ClosestOnFirst, ClosestOnSecond);
            BestDistanceSquared = FMath::Min(BestDistanceSquared, FVector::DistSquared(ClosestOnFirst, ClosestOnSecond));
        }
    }
    
    return BestDistanceSquared;
}

bool FCoverGeometry::EdgeIntersect2D(const FVector& FirstStart, const FVector& FirstEnd, const FVector& SecondStart,
    const FVector& SecondEnd, double& OutFirstFraction)
{
    const FVector2D FirstDirection(FirstEnd.X - FirstStart.X, FirstEnd.Y - FirstStart.Y);
    const FVector2D SecondDirection(SecondEnd.X - SecondStart.X, SecondEnd.Y - SecondStart.Y);
    const FVector2D StartOffset(SecondStart.X - FirstStart.X, SecondStart.Y - FirstStart.Y);

    // The 2D cross product is a single number; its sign is needed for the fractions, so no abs here.
    const double Denominator = FVector2D::CrossProduct(FirstDirection, SecondDirection);
    if (FMath::IsNearlyZero(Denominator))
    {
        return false;
    }

    const double FirstFraction = FVector2D::CrossProduct(StartOffset, SecondDirection) / Denominator;
    const double SecondFraction = FVector2D::CrossProduct(StartOffset, FirstDirection) / Denominator;

    // The lines cross, but the edges only if both fractions stay on their edge.
    if (FirstFraction < 0.0 || FirstFraction > 1.0 || SecondFraction < 0.0 || SecondFraction > 1.0)
    {
        return false;
    }

    OutFirstFraction = FirstFraction;
    return true;
}

void FCoverGeometry::SplitEdgeAtFractions2D(const FVector& EdgeStart, const FVector& EdgeEnd,
    const TArray<double>& Fractions, TArray<FCoverEdgePiece>& OutPieces)
{
    OutPieces.Reset(Fractions.Num() + 1);
    
    // Work on a copy, so the caller's list stays untouched.
    TArray<double> SortedFractions = Fractions;
    SortedFractions.Sort();

    // The borders turn n crossings into n + 1 pieces.
    SortedFractions.Insert(0.0, 0);
    SortedFractions.Add(1.0);

    const FVector EdgeDirection = EdgeEnd - EdgeStart;

    for (int32 PieceIndex = 0; PieceIndex < SortedFractions.Num() - 1; ++PieceIndex)
    {
        const double StartFraction = SortedFractions[PieceIndex];
        const double EndFraction = SortedFractions[PieceIndex + 1];

        // A crossing at an end point or two crossings at the same spot would yield a piece without length.
        if (FMath::IsNearlyEqual(StartFraction, EndFraction, UE_KINDA_SMALL_NUMBER))
        {
            continue;
        }

        FCoverEdgePiece EdgePiece;
        EdgePiece.Start = EdgeStart + EdgeDirection * StartFraction;
        EdgePiece.End = EdgeStart + EdgeDirection * EndFraction;
        OutPieces.Add(EdgePiece);
    }
}

bool FCoverGeometry::IsOnBorder2D(const TArray<FVector>& LoopCorners, const FVector& Point, double BorderTolerance)
{
    // Z is dropped on both sides, the distance is measured in the ground plane only.
    const FVector FlatPoint(Point.X, Point.Y, 0.0);

    for (int32 CornerIndex = 0; CornerIndex < LoopCorners.Num(); ++CornerIndex)
    {
        const FVector& Current = LoopCorners[CornerIndex];
        const FVector& Next = LoopCorners[(CornerIndex + 1) % LoopCorners.Num()];

        const FVector FlatStart(Current.X, Current.Y, 0.0);
        const FVector FlatEnd(Next.X, Next.Y, 0.0);
        if (FMath::PointDistToSegment(FlatPoint, FlatStart, FlatEnd) <= BorderTolerance)
        {
            return true;
        }
    }
    
    return false;
}

bool FCoverGeometry::BuildOffsetPolygon2D(const TArray<FVector>& ConvexCorners, double Offset,
    TArray<FVector>& OutLoop)
{
    OutLoop.Reset();

    const int32 CornerCount = ConvexCorners.Num();
    if (CornerCount < 3)
    {
        return false;
    }

    // The right-hand edge normal below only points outward for positive area, so mirrored footprints get reversed.
    double SignedArea = 0.0;
    for (int32 CornerIndex = 0; CornerIndex < CornerCount; ++CornerIndex)
    {
        const FVector& Current = ConvexCorners[CornerIndex];
        const FVector& Next = ConvexCorners[(CornerIndex + 1) % CornerCount];
        SignedArea += Current.X * Next.Y - Next.X * Current.Y;
    }

    TArray<FVector> OrderedCorners = ConvexCorners;
    if (SignedArea < 0.0)
    {
        Algo::Reverse(OrderedCorners);
    }

    OutLoop.Reserve(CornerCount);
    for (int32 CornerIndex = 0; CornerIndex < CornerCount; ++CornerIndex)
    {
        const FVector& Previous = OrderedCorners[(CornerIndex + CornerCount - 1) % CornerCount];
        const FVector& Current = OrderedCorners[CornerIndex];
        const FVector& Next = OrderedCorners[(CornerIndex + 1) % CornerCount];

        const FVector2D IncomingDirection = FVector2D(Current.X - Previous.X, Current.Y - Previous.Y).GetSafeNormal();
        const FVector2D OutgoingDirection = FVector2D(Next.X - Current.X, Next.Y - Current.Y).GetSafeNormal();
        const FVector2D IncomingNormal(IncomingDirection.Y, -IncomingDirection.X);
        const FVector2D OutgoingNormal(OutgoingDirection.Y, -OutgoingDirection.X);

        // Both edges move by Offset, the new corner lies where the moved edges meet.
        const double MiterDenominator = 1.0 + FVector2D::DotProduct(IncomingNormal, OutgoingNormal);
        if (MiterDenominator < UE_KINDA_SMALL_NUMBER)
        {
            OutLoop.Reset();
            return false;
        }

        const FVector2D MiterOffset = (IncomingNormal + OutgoingNormal) * (Offset / MiterDenominator);
        OutLoop.Emplace(Current.X + MiterOffset.X, Current.Y + MiterOffset.Y, Current.Z);
    }
    return true;
}

double FCoverGeometry::DistanceToLine2D(const FVector& Point, const FVector& LineStart, const FVector& LineEnd)
{
    const FVector2D LineDirection(LineEnd.X - LineStart.X, LineEnd.Y - LineStart.Y);
    const FVector2D ToPoint(Point.X - LineStart.X, Point.Y - LineStart.Y);

    // Without a usable direction there is no line, the distance to the start point is the best answer.
    const double LineLength = LineDirection.Size();
    if (LineLength < UE_KINDA_SMALL_NUMBER)
    {
        return ToPoint.Size();
    }

    // The cross product is the area of the parallelogram, divided by the base it is the height.
    return FMath::Abs(FVector2D::CrossProduct(LineDirection, ToPoint)) / LineLength;
}

void FCoverGeometry::SimplifyPolyline2D(const TArray<FVector>& Points, double Tolerance, TArray<FVector>& OutPoints)
{
    OutPoints.Reset();

    const int32 PointCount = Points.Num();
    if (PointCount < 3)
    {
        OutPoints = Points;
        return;
    }

    TArray<bool> KeepPoints;
    KeepPoints.Init(false, PointCount);
    KeepPoints[0] = true;
    KeepPoints[PointCount - 1] = true;

    // Each entry is a range of indices that still has to be checked against its connecting line.
    TArray<TPair<int32, int32>> RangeStack;
    RangeStack.Emplace(0, PointCount - 1);

    while (!RangeStack.IsEmpty())
    {
        const TPair<int32, int32> Range = RangeStack.Pop();

        double FarthestDistance = 0.0;
        int32 FarthestIndex = INDEX_NONE;
        for (int32 Index = Range.Key + 1; Index < Range.Value; ++Index)
        {
            const double Distance = DistanceToLine2D(Points[Index], Points[Range.Key], Points[Range.Value]);
            if (Distance > FarthestDistance)
            {
                FarthestDistance = Distance;
                FarthestIndex = Index;
            }
        }

        // Everything between the range ends stays dropped, unless one point sticks out too far.
        if (FarthestIndex != INDEX_NONE && FarthestDistance > Tolerance)
        {
            KeepPoints[FarthestIndex] = true;
            RangeStack.Emplace(Range.Key, FarthestIndex);
            RangeStack.Emplace(FarthestIndex, Range.Value);
        }
    }

    for (int32 Index = 0; Index < PointCount; ++Index)
    {
        if (KeepPoints[Index])
        {
            OutPoints.Add(Points[Index]);
        }
    }
}

double FCoverGeometry::Area2D(const TArray<FVector>& Points)
{
    if (Points.Num() < 3)
    {
        return 0.0;
    }

    // Shoelace formula: the sum is twice the signed area, the sign only tells the winding.
    double DoubleSignedArea = 0.0;
    for (int32 PointIndex = 0; PointIndex < Points.Num(); ++PointIndex)
    {
        const FVector& Current = Points[PointIndex];
        const FVector& Next = Points[(PointIndex + 1) % Points.Num()];
        DoubleSignedArea += Current.X * Next.Y - Next.X * Current.Y;
    }

    return FMath::Abs(DoubleSignedArea) * 0.5;
}