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

#if ENABLE_DRAW_DEBUG
    // TEMP: raw data of the outline pipeline, remove after the corner check.
    UE_LOG(LogCover, Log, TEXT("outline: %d grown footprints, %d outer pieces, %d chains"),
           GrownFootprints.Num(), OuterPieces.Num(), ChainedLoops.Num());
    for (const FCoverEdgePiece& Piece : OuterPieces)
    {
        UE_LOG(LogCover, Log, TEXT("  piece from footprint %d: (%.2f, %.2f) -> (%.2f, %.2f)"),
               Piece.SourceIndex, Piece.Start.X, Piece.Start.Y, Piece.End.X, Piece.End.Y);
    }
    for (const FCoverLoop& ChainedLoop : ChainedLoops)
    {
        UE_LOG(LogCover, Log, TEXT("  chain closed=%d, %d raw points"), ChainedLoop.bIsClosed, ChainedLoop.Points.Num());
        for (const FVector& Point : ChainedLoop.Points)
        {
            UE_LOG(LogCover, Log, TEXT("    (%.2f, %.2f)"), Point.X, Point.Y);
        }
    }
#endif

    OutLoops.Reset(ChainedLoops.Num());
    for (const FCoverLoop& ChainedLoop : ChainedLoops)
    {
        FCoverLoop SimplifiedLoop;
        SimplifyLoop(ChainedLoop, SimplifiedLoop);

        // Tiny loops and short chains are leftovers of imprecise placement, not real cover paths.
        const bool bKeep = SimplifiedLoop.bIsClosed
            ? SimplifiedLoop.Points.Num() >= 3
                && FCoverGeometry::ToPolygon2D(SimplifiedLoop.Points).GetArea() >= Settings.OutlineMinLoopArea
            : SimplifiedLoop.Points.Num() >= 2
                && FCoverGeometry::ToPolyline2D(SimplifiedLoop.Points, false).GetLength() >= Settings.OutlineMinChainLength;

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

    // Built once, every edge is tested against the polygons of all other footprints.
    TArray<FPolygon2D> Polygons;
    Polygons.Reserve(Footprints.Num());
    for (const FCoverGrownFootprint& Footprint : Footprints)
    {
        Polygons.Add(FCoverGeometry::ToPolygon2D(Footprint.Corners));
    }

    for (int32 FootprintIndex = 0; FootprintIndex < Footprints.Num(); ++FootprintIndex)
    {
        const FCoverGrownFootprint& Footprint = Footprints[FootprintIndex];
        const TArray<FVector>& Corners = Footprint.Corners;

        for (int32 CornerIndex = 0; CornerIndex < Corners.Num(); ++CornerIndex)
        {
            const FVector& EdgeStart = Corners[CornerIndex];
            const FVector& EdgeEnd = Corners[(CornerIndex + 1) % Corners.Num()];

            // All footprints have positive area, so the right-hand normal points out of the footprint.
            const FSegment2D Edge(FVector2D(EdgeStart.X, EdgeStart.Y), FVector2D(EdgeEnd.X, EdgeEnd.Y));
            const FVector2D OutwardNormal = Edge.GetRightNormal();

            // A disabled side keeps its shape for the inside tests of the neighbors but delivers no pieces.
            const ECoverSide Side = FCoverGeometry::ClassifySide2D(OutwardNormal, Footprint.AxisX, Footprint.AxisY);
            if (!EnumHasAnyFlags(Footprint.EnabledSides, Side))
            {
                continue;
            }

            TArray<double> Alphas;
            for (int32 OtherIndex = 0; OtherIndex < Footprints.Num(); ++OtherIndex)
            {
                if (OtherIndex == FootprintIndex)
                {
                    continue;
                }

                TArray<double> OtherAlphas;
                if (Polygons[OtherIndex].IntersectSegment(Edge, OtherAlphas))
                {
                    Alphas.Append(OtherAlphas);
                }
            }

            // The segment has no height, the pieces take the one of the edge start.
            for (const FSegment2D& PieceSegment : Edge.SplitAtAlphas(Alphas))
            {
                FCoverEdgePiece Piece;
                Piece.Start = FVector(PieceSegment.GetStart(), EdgeStart.Z);
                Piece.End = FVector(PieceSegment.GetEnd(), EdgeStart.Z);

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
        if (!FCoverGeometry::BuildGrownCorners(Corners, Settings.OutlineOffset, Settings.OutlineMiterLimit,
                                               Footprint.Corners))
        {
            continue;
        }

        Footprint.EnabledSides = Member->GetEnabledSides();
        Member->GetSideAxes(Footprint.AxisX, Footprint.AxisY);

        UE_LOG(LogCover, Log, TEXT("footprint %d: sides %d, axis X (%.2f, %.2f), axis Y (%.2f, %.2f)"),
            OutFootprints.Num(), static_cast<int32>(Footprint.EnabledSides),
            Footprint.AxisX.X, Footprint.AxisX.Y, Footprint.AxisY.X, Footprint.AxisY.Y);
#if ENABLE_DRAW_DEBUG
        // TEMP: corners of the grown footprint, remove after the corner check.
        for (const FVector& GrownCorner : Footprint.Corners)
        {
            UE_LOG(LogCover, Log, TEXT("    corner (%.2f, %.2f)"), GrownCorner.X, GrownCorner.Y);
        }
#endif
        OutFootprints.Add(MoveTemp(Footprint));
    }
}

bool FCoverOutlineBuilder::IsPieceOuter(const TArray<FCoverGrownFootprint>& Footprints, int32 OwnFootprintIndex,
    const FVector2D& OutwardNormal, const FVector& MidPoint) const
{
    const double BorderTolerance = Settings.OutlineBorderTolerance;
    const FVector2D FlatMidPoint(MidPoint.X, MidPoint.Y);

    for (int32 OtherIndex = 0; OtherIndex < Footprints.Num(); ++OtherIndex)
    {
        if (OtherIndex == OwnFootprintIndex)
        {
            continue;
        }

        const FCoverGrownFootprint& Other = Footprints[OtherIndex];
        const FPolygon2D OtherPolygon = FCoverGeometry::ToPolygon2D(Other.Corners);

        // Strictly inside: inside and not within the tolerance of the border.
        if (OtherPolygon.ContainsPoint(FlatMidPoint) && !OtherPolygon.IsOnBorder(FlatMidPoint, BorderTolerance))
        {
            return false;
        }

        // Flush neighbors produce the same piece twice. The lower footprint only counts as the keeper
        // if it has this side enabled, otherwise nobody would keep the piece and the outline gets a gap.
        if (OtherIndex < OwnFootprintIndex && OtherPolygon.IsOnBorder(FlatMidPoint, BorderTolerance))
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

    // Point 0 of a closed loop is not necessarily a real corner. The simplification cuts the loop at point 0 and
    // at the point farthest from it, both are far apart and almost always sit on corners, which it always keeps.
    const FPolyline2D Polyline = FCoverGeometry::ToPolyline2D(Loop.Points, Loop.bIsClosed);
    TArray<int32> KeptIndices;
    Polyline.CollectSimplifiedIndices(Settings.OutlineSimplifyTolerance, KeptIndices);

    // The polyline has no height, so the kept points are taken from the loop itself.
    OutLoop.Points.Reserve(KeptIndices.Num());
    for (const int32 KeptIndex : KeptIndices)
    {
        OutLoop.Points.Add(Loop.Points[KeptIndex]);
    }
}
