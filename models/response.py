from datetime import datetime
from typing import Optional, Dict
from bson import ObjectId


class Response:
    collection_name = "responses"
    
    def __init__(
        self,
        user_id: ObjectId,
        task_id: ObjectId,
        assumptions: str,
        architecture: str,
        trade_offs: str,
        failure_scenarios: str,
        submitted_at: datetime = None,
        score: Optional[float] = None,
        score_breakdown: Optional[Dict] = None,
        ai_feedback: Optional[str] = None,
        ai_unlocked_at: Optional[datetime] = None,
        _id: ObjectId = None
    ):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.task_id = task_id
        self.assumptions = assumptions
        self.architecture = architecture
        self.trade_offs = trade_offs
        self.failure_scenarios = failure_scenarios
        self.submitted_at = submitted_at or datetime.utcnow()
        self.score = score
        self.score_breakdown = score_breakdown
        self.ai_feedback = ai_feedback
        self.ai_unlocked_at = ai_unlocked_at
    
    def to_dict(self):
        return {
            "_id": self._id,
            "user_id": self.user_id,
            "task_id": self.task_id,
            "assumptions": self.assumptions,
            "architecture": self.architecture,
            "trade_offs": self.trade_offs,
            "failure_scenarios": self.failure_scenarios,
            "submitted_at": self.submitted_at,
            "score": self.score,
            "score_breakdown": self.score_breakdown,
            "ai_feedback": self.ai_feedback,
            "ai_unlocked_at": self.ai_unlocked_at
        }
    
    @staticmethod
    def from_dict(data: dict):
        return Response(
            _id=data.get("_id"),
            user_id=data["user_id"],
            task_id=data["task_id"],
            assumptions=data["assumptions"],
            architecture=data["architecture"],
            trade_offs=data["trade_offs"],
            failure_scenarios=data["failure_scenarios"],
            submitted_at=data.get("submitted_at"),
            score=data.get("score"),
            score_breakdown=data.get("score_breakdown"),
            ai_feedback=data.get("ai_feedback"),
            ai_unlocked_at=data.get("ai_unlocked_at")
        )
