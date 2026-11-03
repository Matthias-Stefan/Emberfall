// Copyright (c) 2026 Emberfall. All Rights Reserved.

#include "Emberfall/Gameplay/World/Cover/CoverGroup.h"
#include "Emberfall/Gameplay/World/Cover/CoverObject.h"


FCoverGroup::FCoverGroup(int32 InGroupId)
    : GroupId(InGroupId)
{
}

bool FCoverGroup::AddMember(ACoverObject* CoverObject)
{
    if (!IsValid(CoverObject))
    {
        return false;
    }

    const TWeakObjectPtr<ACoverObject> WeakObject(CoverObject);
    if (Members.Contains(WeakObject))
    {
        return false;
    }

    Members.Add(WeakObject);
    return true;
}

bool FCoverGroup::Contains(const ACoverObject* CoverObject) const
{
    return Members.ContainsByPredicate([CoverObject](const TWeakObjectPtr<ACoverObject>& Member)
    {
        return Member.Get() == CoverObject;
    });
}

int32 FCoverGroup::CountLiveMembers() const
{
    int32 LiveMembers = 0;
    for (const TWeakObjectPtr<ACoverObject>& Member : Members)
    {
        if (Member.IsValid())
        {
            ++LiveMembers;
        }
    }
    return LiveMembers;
}