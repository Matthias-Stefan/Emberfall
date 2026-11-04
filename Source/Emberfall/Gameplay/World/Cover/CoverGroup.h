// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

#include "Emberfall/Gameplay/World/Cover/CoverLoop.h"

class ACoverObject;


/**
 * @brief Derived set of cover objects that touch each other; rebuilt on demand, never the source of truth.
 */
class EMBERFALL_API FCoverGroup
{
public:
    /**
     * @brief Creates an empty group.
     * @param InGroupId is the identifier of the group, only stable until the next rebuild.
     */
    explicit FCoverGroup(int32 InGroupId);

    /**
     * @brief Adds a cover object to the group.
     * @param CoverObject is the object to add.
     * @return @c true if it was added, @c false if invalid or already a member.
     */
    bool AddMember(ACoverObject* CoverObject);

    /**
     * @brief Tests whether a cover object belongs to the group.
     * @param CoverObject is the object to look for.
     * @return @c true if it is a member, otherwise @c false.
     */
    bool Contains(const ACoverObject* CoverObject) const;

    /**
     * @brief Counts the members that are still alive.
     * @return Number of valid members.
     */
    int32 CountLiveMembers() const;

    /**
     * @brief Gets the identifier of the group.
     * @return Group id, only stable until the next rebuild.
     */
    int32 GetGroupId() const { return GroupId; }

    /**
     * @brief Replaces the outline loops of the group.
     * @param InLoops is the list of loops to take over.
     */
    void SetLoops(TArray<FCoverLoop>&& InLoops);

    /**
     * @brief Gives read access to the outline loops.
     * @return Loops built by the last rebuild, empty if none were built or the outline is not closed.
     */
    const TArray<FCoverLoop>& GetLoops() const { return Loops; }
    
    /**
     * @brief Gives read access to the members.
     * @return All members, including ones that died since insertion.
     */
    const TArray<TWeakObjectPtr<ACoverObject>>& GetMembers() const { return Members; }

private:
    /** @brief Identifier of this group, only stable until the next rebuild. */
    int32 GroupId = INDEX_NONE;

    /** @brief Cover objects that belong to this group. */
    TArray<TWeakObjectPtr<ACoverObject>> Members;
    
    /** @brief Closed outline loops around the members, derived data that is replaced on every rebuild. */
    TArray<FCoverLoop> Loops;
};