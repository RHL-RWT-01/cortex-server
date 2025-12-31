from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class ResponseBase(BaseModel):
    task_id: str
    assumptions: str
    architecture: str
    architecture_data: Optional[str] = None
    architecture_image: Optional[str] = None
    trade_offs: str
    failure_scenarios: str


class ResponseCreate(ResponseBase):
    pass


class ResponseUpdate(BaseModel):
    assumptions: Optional[str] = None
    architecture: Optional[str] = None
    trade_offs: Optional[str] = None
    failure_scenarios: Optional[str] = None


class ScoreBreakdown(BaseModel):
    clarity: float = Field(..., ge=0, le=10)
    constraints_awareness: float = Field(..., ge=0, le=10)
    trade_off_reasoning: float = Field(..., ge=0, le=10)
    failure_anticipation: float = Field(..., ge=0, le=10)
    simplicity: float = Field(..., ge=0, le=10)
    

class ResponseResponse(ResponseBase):
    id: str
    user_id: str
    submitted_at: datetime
    score: Optional[float] = None
    score_breakdown: Optional[ScoreBreakdown] = None
    ai_feedback: Optional[str] = None
    ai_unlocked_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AIFeedbackRequest(BaseModel):
    response_id: str
