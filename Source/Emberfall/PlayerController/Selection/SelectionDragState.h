// Copyright (c) 2026 Emberfall. All Rights Reserved.

#pragma once


/**
 * @brief Tracks a press-and-drag on the select button and tells a click from a drag.
 */
class FSelectionDragState
{
public:
	FSelectionDragState() = default;
	
	/**
     * @brief Starts tracking when the button goes down.
     * @param StartPos Mouse position in viewport pixels.
     */
	void Begin(FVector2D StartPos);
	
	/**
	 * @brief Sets @c bIsDragging once the mouse is further than @c Threshold from @c DragStart.
	 * @param Current Current mouse position in viewport pixels.
	 * @param Threshold Minimum distance in pixels before a press counts as a drag.
	 */
	void Update(FVector2D Current, float Threshold);
	
	/**
     * @brief Ends tracking when the button goes up.
     * @return @c true if the press was a drag, @c false if it was a click.
     */
	bool Complete();
	
	/** @brief Clears all state. */
	void Reset();
	
	/** @brief Returns @c true while the button is held. */
	bool IsPressed() const { return bPressed; }

	/** @brief Returns @c true once the drag threshold was exceeded. */
	bool IsDragging() const { return bIsDragging; }

	/** @brief Returns the mouse position at the start of the press. */
	FVector2D GetDragStart() const { return DragStart; }
	
protected:
	/** @brief Mouse position when the button went down. */
	FVector2D DragStart{ FVector2D::ZeroVector };

	/** @brief Button is currently held. */
	bool bPressed{ false };

	/** @brief Threshold exceeded; stays @c true until the button is released. */
	bool bIsDragging{ false };
};
