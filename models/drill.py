from datetime import datetime
from typing import List
from bson import ObjectId


class Drill:
    collection_name = "drills"
    
    def __init__(
        self,
        title: str,
        drill_type: str,
        question: str,
        options: List[str],
        correct_answer: str,
        explanation: str,
        created_at: datetime = None,
        _id: ObjectId = None
    ):
        self._id = _id or ObjectId()
        self.title = title
        self.drill_type = drill_type
        self.question = question
        self.options = options
        self.correct_answer = correct_answer
        self.explanation = explanation
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        return {
            "_id": self._id,
            "title": self.title,
            "drill_type": self.drill_type,
            "question": self.question,
            "options": self.options,
            "correct_answer": self.correct_answer,
            "explanation": self.explanation,
            "created_at": self.created_at
        }
    
    @staticmethod
    def from_dict(data: dict):
        return Drill(
            _id=data.get("_id"),
            title=data["title"],
            drill_type=data["drill_type"],
            question=data["question"],
            options=data["options"],
            correct_answer=data["correct_answer"],
            explanation=data["explanation"],
            created_at=data.get("created_at")
        )


class DrillSubmission:
    collection_name = "drill_submissions"
    
    def __init__(
        self,
        user_id: ObjectId,
        drill_id: ObjectId,
        user_answer: str,
        is_correct: bool,
        submitted_at: datetime = None,
        _id: ObjectId = None
    ):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.drill_id = drill_id
        self.user_answer = user_answer
        self.is_correct = is_correct
        self.submitted_at = submitted_at or datetime.utcnow()
    
    def to_dict(self):
        return {
            "_id": self._id,
            "user_id": self.user_id,
            "drill_id": self.drill_id,
            "user_answer": self.user_answer,
            "is_correct": self.is_correct,
            "submitted_at": self.submitted_at
        }
    
    @staticmethod
    def from_dict(data: dict):
        return DrillSubmission(
            _id=data.get("_id"),
            user_id=data["user_id"],
            drill_id=data["drill_id"],
            user_answer=data["user_answer"],
            is_correct=data["is_correct"],
            submitted_at=data.get("submitted_at")
        )
