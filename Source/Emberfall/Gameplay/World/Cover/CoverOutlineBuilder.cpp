// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverOutlineBuilder.h"
#include "Emberfall/Gameplay/World/Cover/CoverGeometry.h"


FCoverOutlineBuilder::FCoverOutlineBuilder(const UCoverSettings& InSettings)
    : Settings(InSettings)
{
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