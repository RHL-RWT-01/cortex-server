"""Progress tracking and streak calculation utilities.

Provides functions for:
- Calculating daily activity streaks
- Updating user progress after task completion
- Managing activity history
"""

from datetime import datetime, date, timedelta, time
from database import get_database
from bson import ObjectId


async def calculate_streak(user_id: ObjectId) -> tuple[int, int]:
    """Calculate current and longest streaks for a user.
    
    A streak is consecutive days where the user completed at least one task.
    Current streak only counts if user was active today or yesterday.
    
    Algorithm:
    1. Get all response dates sorted newest first
    2. Check if streak is still active (today or yesterday)
    3. Count consecutive days backward from most recent
    4. Find longest consecutive sequence in entire history
    
    Args:
        user_id: MongoDB ObjectId of the user
    
    Returns:
        tuple[int, int]: (current_streak, longest_streak)
    """
    db = get_database()
    
    # Get all responses sorted by date
    responses = await db.responses.find(
        {"user_id": user_id}
    ).sort("submitted_at", -1).to_list(length=None)
    
    if not responses:
        return 0, 0
    
    # Extract unique dates
    activity_dates = sorted(set(
        r["submitted_at"].date() for r in responses
    ), reverse=True)
    
    if not activity_dates:
        return 0, 0
    
    # Calculate current streak
    current_streak = 0
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Check if user was active today or yesterday
    if activity_dates[0] == today or activity_dates[0] == yesterday:
        current_streak = 1
        expected_date = activity_dates[0] - timedelta(days=1)
        
        for activity_date in activity_dates[1:]:
            if activity_date == expected_date:
                current_streak += 1
                expected_date -= timedelta(days=1)
            else:
                break
    
    # Calculate longest streak
    longest_streak = 1
    temp_streak = 1
    
    for i in range(len(activity_dates) - 1):
        if (activity_dates[i] - activity_dates[i + 1]).days == 1:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 1
    
    return current_streak, longest_streak


async def update_progress(user_id: ObjectId, score: float):
    """Update user's progress after completing a task.
    
    Updates or creates progress record with:
    - Incremented task count
    - Recalculated streaks
    - Updated score totals and averages
    - Activity history for the day
    
    If this is the user's first task, creates a new progress document.
    Otherwise, updates existing progress with new data.
    
    Args:
        user_id: MongoDB ObjectId of the user
        score: Score earned on this task (average of dimension scores)
    """
    db = get_database()
    
    # Calculate streaks
    current_streak, longest_streak = await calculate_streak(user_id)
    
    # Calculate today's date as a datetime object at midnight for MongoDB compatibility
    today_dt = datetime.combine(date.today(), time.min)
    
    # Get current progress
    progress = await db.progress.find_one({"user_id": user_id})
    
    if progress is None:
        # Create new progress
        new_progress = {
            "user_id": user_id,
            "total_tasks_completed": 1,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "last_activity_date": today_dt,
            "total_score": score,
            "average_score": score,
            "activity_history": [
                {
                    "date": today_dt,
                    "tasks_completed": 1,
                    "score_earned": score
                }
            ]
        }
        await db.progress.insert_one(new_progress)
    else:
        # Update existing progress
        total_tasks = progress["total_tasks_completed"] + 1
        total_score = progress["total_score"] + score
        average_score = total_score / total_tasks
        
        # Update activity history
        activity_history = progress.get("activity_history", [])
        
        # Check if there's already an entry for today
        # Note: We compare with today_dt which is midnight today
        today_entry = next((a for a in activity_history if a["date"] == today_dt), None)
        
        if today_entry:
            today_entry["tasks_completed"] += 1
            today_entry["score_earned"] += score
        else:
            activity_history.append({
                "date": today_dt,
                "tasks_completed": 1,
                "score_earned": score
            })
        
        await db.progress.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "total_tasks_completed": total_tasks,
                    "current_streak": current_streak,
                    "longest_streak": longest_streak,
                    "last_activity_date": today_dt,
                    "total_score": total_score,
                    "average_score": average_score,
                    "activity_history": activity_history
                }
            }
        )
