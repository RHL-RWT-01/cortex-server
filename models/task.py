from datetime import datetime
from typing import List, Optional
from bson import ObjectId


class Task:
    collection_name = "tasks"
    
    def __init__(
        self,
        title: str,
        description: str,
        role: str,
        difficulty: str,
        estimated_time_minutes: int,
        scenario: str,
        prompts: List[str],
        created_at: datetime = None,
        _id: ObjectId = None
    ):
        self._id = _id or ObjectId()
        self.title = title
        self.description = description
        self.role = role
        self.difficulty = difficulty
        self.estimated_time_minutes = estimated_time_minutes
        self.scenario = scenario
        self.prompts = prompts
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        return {
            "_id": self._id,
            "title": self.title,
            "description": self.description,
            "role": self.role,
            "difficulty": self.difficulty,
            "estimated_time_minutes": self.estimated_time_minutes,
            "scenario": self.scenario,
            "prompts": self.prompts,
            "created_at": self.created_at
        }
    
    @staticmethod
    def from_dict(data: dict):
        return Task(
            _id=data.get("_id"),
            title=data["title"],
            description=data["description"],
            role=data["role"],
            difficulty=data["difficulty"],
            estimated_time_minutes=data["estimated_time_minutes"],
            scenario=data["scenario"],
            prompts=data["prompts"],
            created_at=data.get("created_at")
        )
