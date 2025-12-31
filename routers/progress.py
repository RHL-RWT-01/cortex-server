"""User progress tracking routes.

Provides endpoints for:
- Getting user statistics (tasks completed, scores, streaks)
- Calculating current and longest streaks
"""

from fastapi import APIRouter, HTTPException, status, Depends
from database import get_database
from schemas.progress import ProgressResponse
from utils.auth import get_current_user
from utils.progress import calculate_streak

router = APIRouter()


@router.get("/stats", response_model=ProgressResponse)
async def get_progress(
    current_user: dict = Depends(get_current_user)
):
    """Get user's progress statistics and achievements.
    
    Returns comprehensive progress data including:
    - Total tasks completed
    - Current daily streak
    - Longest streak ever
    - Average score
    - Last activity date
    
    Creates initial progress record if user has none.
    Recalculates streaks to ensure accuracy.
    
    Args:
        current_user: Injected current user from JWT token
    
    Returns:
        ProgressResponse: User's progress statistics
    """
    db = get_database()
    
    # Get or create progress
    progress = await db.progress.find_one({"user_id": current_user["_id"]})
    
    if not progress:
        # Initialize progress if not exists
        progress = {
            "user_id": current_user["_id"],
            "total_tasks_completed": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "last_activity_date": None,
            "total_score": 0.0,
            "average_score": 0.0
        }
        await db.progress.insert_one(progress)
    else:
        # Recalculate streaks to ensure accuracy
        current_streak, longest_streak = await calculate_streak(current_user["_id"])
        progress["current_streak"] = current_streak
        progress["longest_streak"] = max(progress.get("longest_streak", 0), longest_streak)
        
        # Update in database
        await db.progress.update_one(
            {"user_id": current_user["_id"]},
            {
                "$set": {
                    "current_streak": current_streak,
                    "longest_streak": progress["longest_streak"]
                }
            }
        )
    
    return {
        "user_id": str(progress["user_id"]),
        "total_tasks_completed": progress["total_tasks_completed"],
        "current_streak": progress["current_streak"],
        "longest_streak": progress["longest_streak"],
        "last_activity_date": progress.get("last_activity_date"),
        "total_score": progress["total_score"],
        "average_score": progress["average_score"]
    }
