from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class ProgressStats(BaseModel):
    total_tasks_completed: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[date] = None
    total_score: float = 0.0
    average_score: float = 0.0


class ProgressResponse(ProgressStats):
    user_id: str
    
    class Config:
        from_attributes = True


class DailyActivity(BaseModel):
    date: date
    tasks_completed: int
    score_earned: float
