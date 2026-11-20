// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverGeometry.h"
#include "Emberfall/Gameplay/World/Cover/CoverTypes.h"


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
        const FVector& Next = QuadCorners[NextIndex(CornerIndex, QuadCorners.Num())];

        const double Side = SideOfEdge2D(Current, Next, Point);
        bHasPositiveSide |= Side > 0.0;
        bHasNegativeSide |= Side < 0.0;
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
        const FVector& Next = QuadCorners[NextIndex(CornerIndex, QuadCorners.Num())];

        // A degenerate edge has no side, so the test cannot give a meaningful answer.
        if (FVector::Dist2D(Current, Next) < UE_KINDA_SMALL_NUMBER)
        {
            return false;
        }

        const double SignedDistance = SignedDistanceToLine2D(Point, Current, Next);
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

bool FCoverGeometry::IsOnBorder2D(const TArray<FVector>& LoopCorners, const FVector& Point, double BorderTolerance)
{
    // Z is dropped on both sides, the distance is measured in the ground plane only.
    const FVector FlatPoint(Point.X, Point.Y, 0.0);

    for (int32 CornerIndex = 0; CornerIndex < LoopCorners.Num(); ++CornerIndex)
    {
        const FVector FlatStart = ToGround(LoopCorners[CornerIndex]);
        const FVector FlatEnd = ToGround(LoopCorners[NextIndex(CornerIndex, LoopCorners.Num())]);
        if (FMath::PointDistToSegment(FlatPoint, FlatStart, FlatEnd) <= BorderTolerance)
        {
            return true;
        }
    }
    
    return false;
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
        const FVector FirstStart = ToGround(FirstQuadCorners[FirstIndex]);
        const FVector FirstEnd = ToGround(FirstQuadCorners[NextIndex(FirstIndex, FirstQuadCorners.Num())]);

        for (int32 SecondIndex = 0; SecondIndex < SecondQuadCorners.Num(); ++SecondIndex)
        {
            const FVector SecondStart = ToGround(SecondQuadCorners[SecondIndex]);
            const FVector SecondEnd = ToGround(SecondQuadCorners[NextIndex(SecondIndex, SecondQuadCorners.Num())]);

            FVector ClosestOnFirst;
            FVector ClosestOnSecond;
            FMath::SegmentDistToSegmentSafe(FirstStart, FirstEnd, SecondStart, SecondEnd, ClosestOnFirst, ClosestOnSecond);
            BestDistanceSquared = FMath::Min(BestDistanceSquared, FVector::DistSquared(ClosestOnFirst, ClosestOnSecond));
        }
    }
    
    return BestDistanceSquared;
}

double FCoverGeometry::DistanceToLine2D(const FVector& Point, const FVector& LineStart, const FVector& LineEnd)
{
    return FMath::Abs(SignedDistanceToLine2D(Point, LineStart, LineEnd));
}

float FCoverGeometry::DistanceSquaredToFootprint2D(
    const FVector& Position, const TArray<FVector>& Corners, FVector2D& OutClosestPoint)
{
    const FVector2D Point(Position.X, Position.Y);
    OutClosestPoint = Point;

    // Too few corners do not form a footprint, report it as infinitely far away.
    if (Corners.Num() < 3)
    {
        return TNumericLimits<float>::Max();
    }

    double BestDistanceSquared = TNumericLimits<double>::Max();

    // Precondition: the footprint is convex. Inside means the point is on the same side of every edge.
    bool bAnyEdgeLeft = false;
    bool bAnyEdgeRight = false;

    for (int32 CornerIndex = 0; CornerIndex < Corners.Num(); ++CornerIndex)
    {
        const FVector& StartCorner = Corners[CornerIndex];
        const FVector& EndCorner = Corners[NextIndex(CornerIndex, Corners.Num())];

        const FVector2D EdgeStart(StartCorner.X, StartCorner.Y);
        const FVector2D Edge = FVector2D(EndCorner.X, EndCorner.Y) - EdgeStart;
        const FVector2D StartToPoint = Point - EdgeStart;

        const double Side = FVector2D::CrossProduct(Edge, StartToPoint);
        bAnyEdgeLeft |= Side > 0.0;
        bAnyEdgeRight |= Side < 0.0;

        const double EdgeLengthSquared = Edge.SizeSquared();

        // A degenerate edge collapses to its start point.
        const double Fraction = EdgeLengthSquared > UE_SMALL_NUMBER
            ? FMath::Clamp(FVector2D::DotProduct(StartToPoint, Edge) / EdgeLengthSquared, 0.0, 1.0)
            : 0.0;

        const FVector2D ClosestOnEdge = EdgeStart + Edge * Fraction;
        const double CandidateDistanceSquared = FVector2D::DistSquared(Point, ClosestOnEdge);
        if (CandidateDistanceSquared < BestDistanceSquared)
        {
            BestDistanceSquared = CandidateDistanceSquared;
            OutClosestPoint = ClosestOnEdge;
        }
    }

    // Never strictly left and strictly right of the edges at once means inside or on the border.
    if (!(bAnyEdgeLeft && bAnyEdgeRight))
    {
        OutClosestPoint = Point;
        return 0.0f;
    }

    return static_cast<float>(BestDistanceSquared);
}

float FCoverGeometry::DistanceSquaredToFootprint2D(const FVector& Position, const TArray<FVector>& Corners)
{
    FVector2D IgnoredClosestPoint;
    return DistanceSquaredToFootprint2D(Position, Corners, IgnoredClosestPoint);
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
    TArray<FVector> OrderedCorners = ConvexCorners;
    if (SignedArea2D(ConvexCorners) < 0.0)
    {
        Algo::Reverse(OrderedCorners);
    }

    OutLoop.Reserve(CornerCount);
    for (int32 CornerIndex = 0; CornerIndex < CornerCount; ++CornerIndex)
    {
        const FVector& Previous = OrderedCorners[PreviousIndex(CornerIndex, CornerCount)];
        const FVector& Current = OrderedCorners[CornerIndex];
        const FVector& Next = OrderedCorners[NextIndex(CornerIndex, CornerCount)];

        const FVector2D IncomingDirection = FVector2D(Current - Previous).GetSafeNormal();
        const FVector2D OutgoingDirection = FVector2D(Next - Current).GetSafeNormal();
        const FVector2D IncomingNormal = RightNormal2D(IncomingDirection);
        const FVector2D OutgoingNormal = RightNormal2D(OutgoingDirection);

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

double FCoverGeometry::Area2D(const TArray<FVector>& Points)
{
    return FMath::Abs(SignedArea2D(Points));
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

double FCoverGeometry::PolylineLength2D(const TArray<FVector>& Points)
{
    double Length = 0.0;
    for (int32 PointIndex = 0; PointIndex + 1 < Points.Num(); ++PointIndex)
    {
        Length += FVector::Dist2D(Points[PointIndex], Points[PointIndex + 1]);
    }
    return Length;
}

//~=============================================================================
// private

int32 FCoverGeometry::NextIndex(int32 Index, int32 Count)
{
    return Index + 1 == Count ? 0 : Index + 1;
}

int32 FCoverGeometry::PreviousIndex(int32 Index, int32 Count)
{
    return Index == 0 ? Count - 1 : Index - 1;
}

FVector FCoverGeometry::ToGround(const FVector& Point)
{
    return FVector(Point.X, Point.Y, 0.0);
}

double FCoverGeometry::SignedArea2D(const TArray<FVector>& Points)
{
    if (Points.Num() < 3)
    {
        return 0.0;
    }

    // Shoelace formula: the sum is twice the signed area, positive for counterclockwise winding.
    double DoubleSignedArea = 0.0;
    for (int32 PointIndex = 0; PointIndex < Points.Num(); ++PointIndex)
    {
        const FVector& Current = Points[PointIndex];
        const FVector& Next = Points[NextIndex(PointIndex, Points.Num())];
        DoubleSignedArea += Current.X * Next.Y - Next.X * Current.Y;
    }

    return DoubleSignedArea * 0.5;
}

double FCoverGeometry::SideOfEdge2D(const FVector& EdgeStart, const FVector& EdgeEnd, const FVector& Point)
{
    return (EdgeEnd.X - EdgeStart.X) * (Point.Y - EdgeStart.Y) - (EdgeEnd.Y - EdgeStart.Y) * (Point.X - EdgeStart.X);
}

double FCoverGeometry::SignedDistanceToLine2D(const FVector& Point, const FVector& LineStart, const FVector& LineEnd)
{
    const double LineLength = FVector::Dist2D(LineStart, LineEnd);

    // Without a usable direction there is no line, the distance to the start point is the best answer.
    if (LineLength < UE_KINDA_SMALL_NUMBER)
    {
        return FVector::Dist2D(Point, LineStart);
    }

    // The cross product is the area of the parallelogram, divided by the base it is the signed height.
    return SideOfEdge2D(LineStart, LineEnd, Point) / LineLength;
}

FVector2D FCoverGeometry::RightNormal2D(const FVector2D& Direction)
{
    return FVector2D(Direction.Y, -Direction.X);
}
