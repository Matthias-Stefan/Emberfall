// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverOutlineBuilder.h"

#include "CoverObject.h"
#include "Emberfall/Gameplay/World/Cover/CoverGeometry.h"
#include "Emberfall/Gameplay/World/Cover/CoverGroup.h"
#include "Emberfall/Gameplay/World/Cover/CoverLoop.h"

FCoverOutlineBuilder::FCoverOutlineBuilder(const UCoverSettings& InSettings)
    : Settings(InSettings)
{
    ensureMsgf(InSettings.OutlineOffset >= InSettings.MergeRadius * 0.5f,
        TEXT("OutlineOffset (%.1f) must be at least half of MergeRadius (%.1f), otherwise groups split into several outlines."),
        InSettings.OutlineOffset, InSettings.MergeRadius);
}

void FCoverOutlineBuilder::Build(const FCoverGroup& Group, TArray<FCoverLoop>& OutLoops) const
{
    TArray<TArray<FVector>> GrownFootprints;
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

        // Tiny loops are gaps from imprecise placement, not real courtyards.
        if (SimplifiedLoop.Points.Num() >= 3
            && FCoverGeometry::Area2D(SimplifiedLoop.Points) >= Settings.OutlineMinLoopArea)
        {
            OutLoops.Add(MoveTemp(SimplifiedLoop));
        }
    }
}

void FCoverOutlineBuilder::FilterOuterPieces(const TArray<TArray<FVector>>& Loops,
                                             TArray<FCoverEdgePiece>& OutPieces) const
{
    OutPieces.Reset();

    for (int32 LoopIndex = 0; LoopIndex < Loops.Num(); ++LoopIndex)
    {
        const TArray<FVector>& Loop = Loops[LoopIndex];

        for (int32 CornerIndex = 0; CornerIndex < Loop.Num(); ++CornerIndex)
        {
            const FVector& EdgeStart = Loop[CornerIndex];
            const FVector& EdgeEnd = Loop[(CornerIndex + 1) % Loop.Num()];

            TArray<double> Fractions;
            for (int32 OtherLoopIndex = 0; OtherLoopIndex < Loops.Num(); ++OtherLoopIndex)
            {
                if (OtherLoopIndex == LoopIndex)
                {
                    continue;
                }

                const TArray<FVector>& OtherLoop = Loops[OtherLoopIndex];
                for (int32 OtherCornerIndex = 0; OtherCornerIndex < OtherLoop.Num(); ++OtherCornerIndex)
                {
                    double Fraction = 0.0;
                    if (FCoverGeometry::EdgeIntersect2D(
                            EdgeStart, EdgeEnd,
                            OtherLoop[OtherCornerIndex],
                            OtherLoop[(OtherCornerIndex + 1) % OtherLoop.Num()],
                            Fraction))
                    {
                        Fractions.Add(Fraction);
                    }
                }
            }

            TArray<FCoverEdgePiece> Pieces;
            FCoverGeometry::SplitEdgeAtFractions2D(EdgeStart, EdgeEnd, Fractions, Pieces);

            for (const FCoverEdgePiece& Piece : Pieces)
            {
                const FVector MidPoint = (Piece.Start + Piece.End) * 0.5;
                if (IsPieceOuter(Loops, LoopIndex, MidPoint))
                {
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

            int32 NextIndex = INDEX_NONE;
            for (int32 CandidateIndex = 0; CandidateIndex < Pieces.Num(); ++CandidateIndex)
            {
                if (!UsedPieces[CandidateIndex] && IsNear(Pieces[CandidateIndex].Start, CurrentEnd))
                {
                    NextIndex = CandidateIndex;
                    break;
                }
            }

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
            UE_LOG(LogTemp, Warning, TEXT("FCoverOutlineBuilder: chain of %d points is not closed, dropped"), Loop.Points.Num());
        }
    }
}

void FCoverOutlineBuilder::BuildGrownFootprints(const FCoverGroup& Group, TArray<TArray<FVector>>& OutFootprints) const
{
    OutFootprints.Reset();
    
    for (const TWeakObjectPtr<ACoverObject>& WeakMember : Group.GetMembers())
    {
        const ACoverObject* Member = WeakMember.Get();
        if (Member == nullptr)
        {
            continue;;
        }
        
        TArray<FVector> Corners;
        if (!Member->GetFootprintCorners(Corners))
        {
            continue;
        }
        
        // Members without a mesh or with a spiked corner are skipped, so the index in OutFootprints can differ from the index in the group.
        TArray<FVector> GrownFootprint;
        if (!FCoverGeometry::BuildOffsetPolygon2D(Corners, Settings.OutlineOffset, GrownFootprint))
        {
            continue;
        }

        OutFootprints.Add(MoveTemp(GrownFootprint));
    }
}

bool FCoverOutlineBuilder::IsPieceOuter(const TArray<TArray<FVector>>& Loops, int32 OwnLoopIndex,
                                        const FVector& MidPoint) const
{
    const double BorderTolerance = Settings.OutlineBorderTolerance;

    for (int32 OtherLoopIndex = 0; OtherLoopIndex < Loops.Num(); ++OtherLoopIndex)
    {
        if (OtherLoopIndex == OwnLoopIndex)
        {
            continue;
        }

        const TArray<FVector>& OtherLoop = Loops[OtherLoopIndex];
        if (FCoverGeometry::ContainsPointStrict2D(OtherLoop, MidPoint, BorderTolerance))
        {
            return false;
        }

        // Flush neighbors produce the same piece twice, the loop with the lower index keeps it.
        if (OtherLoopIndex < OwnLoopIndex && FCoverGeometry::IsOnBorder2D(OtherLoop, MidPoint, BorderTolerance))
        {
            return false;
        }
    }
    return true;
}

void FCoverOutlineBuilder::SimplifyLoop(const FCoverLoop& Loop, FCoverLoop& OutLoop) const
{
    OutLoop.Points.Reset();

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
