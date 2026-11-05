// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverOutlineBuilder.h"
#include "Emberfall/Gameplay/World/Cover/CoverGeometry.h"
#include "Emberfall/Gameplay/World/Cover/CoverGroup.h"
#include "Emberfall/Gameplay/World/Cover/CoverLog.h"
#include "Emberfall/Gameplay/World/Cover/CoverObject.h"
#include "Emberfall/Gameplay/World/Cover/CoverTypes.h"


FCoverOutlineBuilder::FCoverOutlineBuilder(const UCoverSettings& InSettings)
    : Settings(InSettings)
{
    ensureMsgf(InSettings.OutlineOffset >= InSettings.MergeRadius * 0.5f,
               TEXT(
                   "OutlineOffset (%.1f) must be at least half of MergeRadius (%.1f), otherwise groups split into several outlines."
               ),
               InSettings.OutlineOffset, InSettings.MergeRadius);
}

void FCoverOutlineBuilder::Build(const FCoverGroup& Group, TArray<FCoverLoop>& OutLoops) const
{
    TArray<FCoverGrownFootprint> GrownFootprints;
    BuildGrownFootprints(Group, GrownFootprints);

    TArray<FCoverEdgePiece> OuterPieces;
    FilterOuterPieces(GrownFootprints, OuterPieces);

    TArray<FCoverLoop> ChainedLoops;
    ChainPieces(OuterPieces, ChainedLoops);

    OutLoops.Reset(ChainedLoops.Num());
    for (const FCoverLoop& ChainedLoop : ChainedLoops)
    {
        FCoverLoop SimplifiedLoop;
        SimplifyLoop(ChainedLoop, SimplifiedLoop);

        // Tiny loops and short chains are leftovers of imprecise placement, not real cover paths.
        const bool bKeep = SimplifiedLoop.bIsClosed
            ? SimplifiedLoop.Points.Num() >= 3
                && FCoverGeometry::Area2D(SimplifiedLoop.Points) >= Settings.OutlineMinLoopArea
            : SimplifiedLoop.Points.Num() >= 2
                && FCoverGeometry::PolylineLength2D(SimplifiedLoop.Points) >= Settings.OutlineMinChainLength;

        if (bKeep)
        {
            OutLoops.Add(MoveTemp(SimplifiedLoop));
        }
    }
}

void FCoverOutlineBuilder::FilterOuterPieces(const TArray<FCoverGrownFootprint>& Footprints,
                                             TArray<FCoverEdgePiece>& OutPieces) const
{
    OutPieces.Reset();

    for (int32 FootprintIndex = 0; FootprintIndex < Footprints.Num(); ++FootprintIndex)
    {
        const FCoverGrownFootprint& Footprint = Footprints[FootprintIndex];
        const TArray<FVector>& Corners = Footprint.Corners;

        for (int32 CornerIndex = 0; CornerIndex < Corners.Num(); ++CornerIndex)
        {
            const FVector& EdgeStart = Corners[CornerIndex];
            const FVector& EdgeEnd = Corners[(CornerIndex + 1) % Corners.Num()];

            // All footprints have positive area, so the right-hand normal points out of the footprint.
            const FVector2D EdgeDirection =
                FVector2D(EdgeEnd.X - EdgeStart.X, EdgeEnd.Y - EdgeStart.Y).GetSafeNormal();
            const FVector2D OutwardNormal(EdgeDirection.Y, -EdgeDirection.X);

            // A disabled side keeps its shape for the inside tests of the neighbors but delivers no pieces.
            const ECoverSide Side = FCoverGeometry::ClassifySide2D(OutwardNormal, Footprint.AxisX, Footprint.AxisY);
            if (!EnumHasAnyFlags(Footprint.EnabledSides, Side))
            {
                continue;
            }

            TArray<double> Fractions;
            for (int32 OtherIndex = 0; OtherIndex < Footprints.Num(); ++OtherIndex)
            {
                if (OtherIndex == FootprintIndex)
                {
                    continue;
                }

                const TArray<FVector>& OtherCorners = Footprints[OtherIndex].Corners;
                for (int32 OtherCornerIndex = 0; OtherCornerIndex < OtherCorners.Num(); ++OtherCornerIndex)
                {
                    double Fraction = 0.0;
                    if (FCoverGeometry::EdgeIntersect2D(
                            EdgeStart, EdgeEnd,
                            OtherCorners[OtherCornerIndex],
                            OtherCorners[(OtherCornerIndex + 1) % OtherCorners.Num()],
                            Fraction))
                    {
                        Fractions.Add(Fraction);
                    }
                }
            }

            TArray<FCoverEdgePiece> Pieces;
            FCoverGeometry::SplitEdgeAtFractions2D(EdgeStart, EdgeEnd, Fractions, Pieces);

            // Copy on purpose, the piece gets the index of its footprint before it is stored.
            for (FCoverEdgePiece Piece : Pieces)
            {
                const FVector MidPoint = (Piece.Start + Piece.End) * 0.5;
                if (IsPieceOuter(Footprints, FootprintIndex, OutwardNormal, MidPoint))
                {
                    Piece.SourceIndex = FootprintIndex;
                    OutPieces.Add(Piece);
                }
            }
        }
    }
}

void FCoverOutlineBuilder::ChainPieces(const TArray<FCoverEdgePiece>& Pieces, TArray<FCoverLoop>& OutLoops) const
{
    OutLoops.Reset();

    TArray<bool> UsedPieces;
    UsedPieces.Init(false, Pieces.Num());

    // Compared as squared distances in the ground plane, so no square root is needed.
    const double ToleranceSquared = FMath::Square(static_cast<double>(Settings.OutlineBorderTolerance));
    auto IsNear = [ToleranceSquared](const FVector& First, const FVector& Second)
    {
        return FVector::DistSquared2D(First, Second) <= ToleranceSquared;
    };

    // Finds the first unused piece that starts at the given point, INDEX_NONE if there is none.
    auto FindNextPiece = [&](const FVector& Point)
    {
        for (int32 CandidateIndex = 0; CandidateIndex < Pieces.Num(); ++CandidateIndex)
        {
            if (!UsedPieces[CandidateIndex] && IsNear(Pieces[CandidateIndex].Start, Point))
            {
                return CandidateIndex;
            }
        }
        return static_cast<int32>(INDEX_NONE);
    };

    // Phase A: a piece without predecessor is the start of an open chain.
    TArray<bool> HasPredecessor;
    HasPredecessor.Init(false, Pieces.Num());
    for (int32 PieceIndex = 0; PieceIndex < Pieces.Num(); ++PieceIndex)
    {
        for (int32 OtherIndex = 0; OtherIndex < Pieces.Num(); ++OtherIndex)
        {
            if (OtherIndex != PieceIndex && IsNear(Pieces[OtherIndex].End, Pieces[PieceIndex].Start))
            {
                HasPredecessor[PieceIndex] = true;
                break;
            }
        }
    }

    // Phase B: open chains first, otherwise a closed-loop search could start in the middle of one and never close.
    for (int32 PieceIndex = 0; PieceIndex < Pieces.Num(); ++PieceIndex)
    {
        if (UsedPieces[PieceIndex] || HasPredecessor[PieceIndex])
        {
            continue;
        }

        UsedPieces[PieceIndex] = true;

        FCoverLoop Chain;
        Chain.bIsClosed = false;
        Chain.Points.Add(Pieces[PieceIndex].Start);
        FVector CurrentEnd = Pieces[PieceIndex].End;

        for (int32 NextIndex = FindNextPiece(CurrentEnd); NextIndex != INDEX_NONE; NextIndex = FindNextPiece(CurrentEnd))
        {
            UsedPieces[NextIndex] = true;
            Chain.Points.Add(Pieces[NextIndex].Start);
            CurrentEnd = Pieces[NextIndex].End;
        }

        // An open chain keeps its end point, otherwise the last piece of line is missing.
        Chain.Points.Add(CurrentEnd);
        OutLoops.Add(MoveTemp(Chain));
    }

    // Phase C: what is left has a predecessor everywhere, so it can only form closed loops.
    for (int32 PieceIndex = 0; PieceIndex < Pieces.Num(); ++PieceIndex)
    {
        if (UsedPieces[PieceIndex])
        {
            continue;
        }

        UsedPieces[PieceIndex] = true;

        FCoverLoop Loop;
        const FVector LoopStart = Pieces[PieceIndex].Start;
        FVector CurrentEnd = Pieces[PieceIndex].End;
        bool bClosed = false;

        Loop.Points.Add(LoopStart);

        for (;;)
        {
            // Check first, otherwise the search could pick up a foreign piece that starts at the closing point.
            if (IsNear(CurrentEnd, LoopStart))
            {
                bClosed = true;
                break;
            }

            const int32 NextIndex = FindNextPiece(CurrentEnd);
            if (NextIndex == INDEX_NONE)
            {
                break;
            }

            UsedPieces[NextIndex] = true;
            Loop.Points.Add(Pieces[NextIndex].Start);
            CurrentEnd = Pieces[NextIndex].End;
        }

        if (bClosed)
        {
            OutLoops.Add(MoveTemp(Loop));
        }
        else
        {
            UE_LOG(LogCover, Warning, TEXT("FCoverOutlineBuilder: chain of %d points does not close, dropped"),
                   Loop.Points.Num());
        }
    }
}

void FCoverOutlineBuilder::BuildGrownFootprints(const FCoverGroup& Group,
                                                TArray<FCoverGrownFootprint>& OutFootprints) const
{
    OutFootprints.Reset();

    for (const TWeakObjectPtr<ACoverObject>& WeakMember : Group.GetMembers())
    {
        const ACoverObject* Member = WeakMember.Get();
        if (!Member)
        {
            continue;
        }

        TArray<FVector> Corners;
        if (!Member->GetFootprintCorners(Corners))
        {
            continue;
        }

        FCoverGrownFootprint Footprint;
        if (!FCoverGeometry::BuildOffsetPolygon2D(Corners, Settings.OutlineOffset, Footprint.Corners))
        {
            continue;
        }

        Footprint.EnabledSides = Member->GetEnabledSides();
        Member->GetSideAxes(Footprint.AxisX, Footprint.AxisY);

        UE_LOG(LogCover, Log, TEXT("footprint %d: sides %d, axis X (%.2f, %.2f), axis Y (%.2f, %.2f)"),
            OutFootprints.Num(), static_cast<int32>(Footprint.EnabledSides),
            Footprint.AxisX.X, Footprint.AxisX.Y, Footprint.AxisY.X, Footprint.AxisY.Y);
        OutFootprints.Add(MoveTemp(Footprint));
    }
}

bool FCoverOutlineBuilder::IsPieceOuter(const TArray<FCoverGrownFootprint>& Footprints, int32 OwnFootprintIndex,
    const FVector2D& OutwardNormal, const FVector& MidPoint) const
{
    const double BorderTolerance = Settings.OutlineBorderTolerance;

    for (int32 OtherIndex = 0; OtherIndex < Footprints.Num(); ++OtherIndex)
    {
        if (OtherIndex == OwnFootprintIndex)
        {
            continue;
        }

        const FCoverGrownFootprint& Other = Footprints[OtherIndex];
        if (FCoverGeometry::ContainsPointStrict2D(Other.Corners, MidPoint, BorderTolerance))
        {
            return false;
        }

        // Flush neighbors produce the same piece twice. The lower footprint only counts as the keeper
        // if it has this side enabled, otherwise nobody would keep the piece and the outline gets a gap.
        if (OtherIndex < OwnFootprintIndex && FCoverGeometry::IsOnBorder2D(Other.Corners, MidPoint, BorderTolerance))
        {
            const ECoverSide OtherSide = FCoverGeometry::ClassifySide2D(OutwardNormal, Other.AxisX, Other.AxisY);
            if (EnumHasAnyFlags(Other.EnabledSides, OtherSide))
            {
                return false;
            }
        }
    }
    return true;
}

void FCoverOutlineBuilder::SimplifyLoop(const FCoverLoop& Loop, FCoverLoop& OutLoop) const
{
    OutLoop.bIsClosed = Loop.bIsClosed;
    OutLoop.Points.Reset();

    if (!Loop.bIsClosed)
    {
        FCoverGeometry::SimplifyPolyline2D(Loop.Points, Settings.OutlineSimplifyTolerance, OutLoop.Points);
        return;
    }
    
    const TArray<FVector>& Points = Loop.Points;
    const int32 PointCount = Points.Num();
    if (PointCount < 4)
    {
        OutLoop.Points = Points;
        return;
    }

    // Point 0 is not necessarily a real corner, so the loop is cut at point 0 and at the point farthest from it.
    // Both are far apart and almost always sit on corners, which the simplification always keeps.
    int32 SplitIndex = INDEX_NONE;
    double FarthestDistanceSquared = 0.0;
    for (int32 PointIndex = 1; PointIndex < PointCount; ++PointIndex)
    {
        const double DistanceSquared = FVector::DistSquared2D(Points[0], Points[PointIndex]);
        if (DistanceSquared > FarthestDistanceSquared)
        {
            FarthestDistanceSquared = DistanceSquared;
            SplitIndex = PointIndex;
        }
    }

    if (SplitIndex == INDEX_NONE)
    {
        OutLoop.Points = Points;
        return;
    }

    // First half runs from point 0 to the split point, second half from the split point back around to point 0.
    TArray<FVector> FirstHalf;
    for (int32 PointIndex = 0; PointIndex <= SplitIndex; ++PointIndex)
    {
        FirstHalf.Add(Points[PointIndex]);
    }

    TArray<FVector> SecondHalf;
    for (int32 PointIndex = SplitIndex; PointIndex < PointCount; ++PointIndex)
    {
        SecondHalf.Add(Points[PointIndex]);
    }
    SecondHalf.Add(Points[0]);

    const double Tolerance = Settings.OutlineSimplifyTolerance;
    TArray<FVector> SimplifiedFirstHalf;
    TArray<FVector> SimplifiedSecondHalf;
    FCoverGeometry::SimplifyPolyline2D(FirstHalf, Tolerance, SimplifiedFirstHalf);
    FCoverGeometry::SimplifyPolyline2D(SecondHalf, Tolerance, SimplifiedSecondHalf);

    // The split point ends the first half and starts the second, point 0 ends the second half and starts the first.
    // Each is taken once, so no zero-length edge appears.
    OutLoop.Points = SimplifiedFirstHalf;
    for (int32 PointIndex = 1; PointIndex < SimplifiedSecondHalf.Num() - 1; ++PointIndex)
    {
        OutLoop.Points.Add(SimplifiedSecondHalf[PointIndex]);
    }
}
