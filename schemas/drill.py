from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DrillType(str, Enum):
    ASSUMPTIONS = "spot_assumptions"
    FAILURE_MODES = "rank_failures"
    SCALING = "predict_scaling"
    TRADE_OFFS = "choose_tradeoffs"


class DrillBase(BaseModel):
    title: str
    drill_type: DrillType
    question: str
    options: List[str]  # Multiple choice or ranking options
    correct_answer: str  # For validation
    explanation: str


class DrillCreate(DrillBase):
    pass


class DrillResponse(DrillBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class DrillSubmission(BaseModel):
    drill_id: str
    user_answer: str


class DrillResult(BaseModel):
    is_correct: bool
    explanation: str
    user_answer: str
    correct_answer: str
