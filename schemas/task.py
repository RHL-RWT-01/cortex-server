from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Role(str, Enum):
    BACKEND = "Backend Engineer"
    FRONTEND = "Frontend Engineer"
    FULLSTACK = "Fullstack Engineer"
    SYSTEMS = "Systems Engineer"
    DATA = "Data Engineer"
    DEVOPS = "DevOps Engineer"
    SECURITY = "Security Engineer"


class TaskBase(BaseModel):
    title: str
    description: str
    role: Role
    difficulty: Difficulty
    estimated_time_minutes: int
    scenario: str
    prompts: List[str]  # Questions to guide thinking
    

class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[Difficulty] = None
    estimated_time_minutes: Optional[int] = None
    scenario: Optional[str] = None
    prompts: Optional[List[str]] = None


class TaskResponse(TaskBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TaskFilter(BaseModel):
    role: Optional[Role] = None
    difficulty: Optional[Difficulty] = None
