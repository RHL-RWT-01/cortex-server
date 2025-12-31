from datetime import datetime, date
from typing import Optional, List, Dict
from bson import ObjectId


class Progress:
    collection_name = "progress"
    
    def __init__(
        self,
        user_id: ObjectId,
        total_tasks_completed: int = 0,
        current_streak: int = 0,
        longest_streak: int = 0,
        last_activity_date: Optional[date] = None,
        total_score: float = 0.0,
        average_score: float = 0.0,
        activity_history: List[Dict] = None,
        _id: ObjectId = None
    ):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.total_tasks_completed = total_tasks_completed
        self.current_streak = current_streak
        self.longest_streak = longest_streak
        self.last_activity_date = last_activity_date
        self.total_score = total_score
        self.average_score = average_score
        self.activity_history = activity_history or []
    
    def to_dict(self):
        return {
            "_id": self._id,
            "user_id": self.user_id,
            "total_tasks_completed": self.total_tasks_completed,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "last_activity_date": self.last_activity_date,
            "total_score": self.total_score,
            "average_score": self.average_score,
            "activity_history": self.activity_history
        }
    
    @staticmethod
    def from_dict(data: dict):
        return Progress(
            _id=data.get("_id"),
            user_id=data["user_id"],
            total_tasks_completed=data.get("total_tasks_completed", 0),
            current_streak=data.get("current_streak", 0),
            longest_streak=data.get("longest_streak", 0),
            last_activity_date=data.get("last_activity_date"),
            total_score=data.get("total_score", 0.0),
            average_score=data.get("average_score", 0.0),
            activity_history=data.get("activity_history", [])
        )
