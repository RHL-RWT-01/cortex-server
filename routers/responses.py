"""Response submission and AI feedback routes.

Provides endpoints for:
- Submitting responses to tasks
- Requesting AI feedback (time-gated)
- Viewing response history
- Getting specific response details
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import List
from datetime import datetime, timedelta
from database import get_database
from schemas.response import (
    ResponseCreate,
    ResponseResponse,
    AIFeedbackRequest,
    ScoreBreakdown
)
from utils.auth import get_current_user
from utils.ai import generate_ai_feedback, calculate_reasoning_score
from utils.progress import update_progress
from utils.subscription import check_task_limit
from bson import ObjectId
from logger import get_logger
from utils.rate_limit import limiter

logger = get_logger(__name__)
router = APIRouter()


@router.post("", response_model=ResponseResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def submit_response(
    request: Request,
    response: ResponseCreate,
    current_user: dict = Depends(get_current_user)
):
    """Submit a response to an engineering task.
    
    Processes user's response and:
    - Validates the task exists
    - Calculates AI-powered scores across 5 dimensions
    - Saves the response to database
    - Updates user's progress statistics
    
    AI feedback is not immediately available - user must wait 5 minutes.
    
    Args:
        response: User's response (assumptions, architecture, tradeoffs, failures)
        current_user: Injected current user from JWT token
    
    Returns:
        ResponseResponse: Submitted response with scores
    
    Raises:
        HTTPException 400: If task ID is invalid
        HTTPException 403: If user has exceeded task limit
        HTTPException 404: If task not found
    """
    db = get_database()
    
    # Check subscription limits
    can_submit, limit_message = await check_task_limit(current_user["_id"])
    if not can_submit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": limit_message,
                "upgrade_required": True,
                "error_code": "TASK_LIMIT_EXCEEDED"
            }
        )
    
    # Verify task exists
    try:
        task = await db.tasks.find_one({"_id": ObjectId(response.task_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID"
        )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Calculate scores using AI
    scores = await calculate_reasoning_score(
        response.assumptions,
        response.architecture,
        response.trade_offs,
        response.failure_scenarios,
        response.architecture_image,
        task_scenario=task["scenario"],
        task_prompts=task["prompts"]
    )
    
    # Calculate total score (average of all dimensions)
    total_score = sum(scores.values()) / len(scores)
    
    # Create response document
    response_data = {
        "user_id": current_user["_id"],
        "task_id": ObjectId(response.task_id),
        "assumptions": response.assumptions,
        "architecture": response.architecture,
        "architecture_data": response.architecture_data,
        "architecture_image": response.architecture_image,
        "trade_offs": response.trade_offs,
        "failure_scenarios": response.failure_scenarios,
        "submitted_at": datetime.utcnow(),
        "score": round(total_score, 2),
        "score_breakdown": scores,
        "ai_feedback": None,
        "ai_unlocked_at": None
    }
    
    result = await db.responses.insert_one(response_data)
    response_data["_id"] = result.inserted_id
    
    # Update user progress
    await update_progress(current_user["_id"], total_score)
    
    return {
        "id": str(response_data["_id"]),
        "user_id": str(response_data["user_id"]),
        "task_id": response.task_id,
        "assumptions": response_data["assumptions"],
        "architecture": response_data["architecture"],
        "architecture_data": response_data["architecture_data"],
        "architecture_image": response_data["architecture_image"],
        "trade_offs": response_data["trade_offs"],
        "failure_scenarios": response_data["failure_scenarios"],
        "submitted_at": response_data["submitted_at"],
        "score": response_data["score"],
        "score_breakdown": ScoreBreakdown(**scores),
        "ai_feedback": response_data["ai_feedback"],
        "ai_unlocked_at": response_data["ai_unlocked_at"]
    }


@router.post("/{response_id}/feedback")
@limiter.limit("5/minute")
async def request_ai_feedback(
    request: Request,
    response_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Request AI feedback for a response (time-gated)"""
    db = get_database()
    
    # Get response
    try:
        response = await db.responses.find_one({"_id": ObjectId(response_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid response ID"
        )
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found"
        )
    
    # Verify ownership
    if response["user_id"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this response"
        )
    
    # Check if AI feedback already exists
    if response.get("ai_feedback"):
        return {
            "message": "AI feedback already generated",
            "feedback": response["ai_feedback"],
            "unlocked_at": response.get("ai_unlocked_at")
        }
    
    # Time-gate check: Must wait 5 minutes after submission
    time_since_submission = datetime.utcnow() - response["submitted_at"]
    if time_since_submission < timedelta(minutes=5):
        remaining = timedelta(minutes=5) - time_since_submission
        raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail=f"AI feedback unlocks in {int(remaining.total_seconds() / 60)} minutes"
        )
    
    # Get task for context
    task = await db.tasks.find_one({"_id": response["task_id"]})
    
    # Generate AI feedback
    feedback = await generate_ai_feedback(
        task["scenario"],
        task["prompts"],
        response["assumptions"],
        response["architecture"],
        response["trade_offs"],
        response["failure_scenarios"],
        response.get("architecture_image")
    )
    
    # Update response with feedback
    await db.responses.update_one(
        {"_id": response["_id"]},
        {
            "$set": {
                "ai_feedback": feedback,
                "ai_unlocked_at": datetime.utcnow()
            }
        }
    )
    
    return {
        "message": "AI feedback generated successfully",
        "feedback": feedback,
        "unlocked_at": datetime.utcnow()
    }


@router.get("/user/history", response_model=List[ResponseResponse])
@limiter.limit("30/minute")
async def get_user_responses(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get all responses submitted by current user"""
    db = get_database()
    
    responses = await db.responses.find(
        {"user_id": current_user["_id"]}
    ).sort("submitted_at", -1).to_list(length=None)
    
    return [
        {
            "id": str(r["_id"]),
            "user_id": str(r["user_id"]),
            "task_id": str(r["task_id"]),
            "assumptions": r["assumptions"],
            "architecture": r["architecture"],
            "architecture_data": r.get("architecture_data"),
            "architecture_image": r.get("architecture_image"),
            "trade_offs": r["trade_offs"],
            "failure_scenarios": r["failure_scenarios"],
            "submitted_at": r["submitted_at"],
            "score": r.get("score"),
            "score_breakdown": ScoreBreakdown(**r["score_breakdown"]) if r.get("score_breakdown") else None,
            "ai_feedback": r.get("ai_feedback"),
            "ai_unlocked_at": r.get("ai_unlocked_at")
        }
        for r in responses
    ]


@router.get("/{response_id}", response_model=ResponseResponse)
async def get_response(
    response_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific response"""
    db = get_database()
    
    try:
        response = await db.responses.find_one({"_id": ObjectId(response_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid response ID"
        )
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found"
        )
    
    # Verify ownership
    if response["user_id"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this response"
        )
    
    return {
        "id": str(response["_id"]),
        "user_id": str(response["user_id"]),
        "task_id": str(response["task_id"]),
        "assumptions": response["assumptions"],
        "architecture": response["architecture"],
        "architecture_data": response.get("architecture_data"),
        "architecture_image": response.get("architecture_image"),
        "trade_offs": response["trade_offs"],
        "failure_scenarios": response["failure_scenarios"],
        "submitted_at": response["submitted_at"],
        "score": response.get("score"),
        "score_breakdown": ScoreBreakdown(**response["score_breakdown"]) if response.get("score_breakdown") else None,
        "ai_feedback": response.get("ai_feedback"),
        "ai_unlocked_at": response.get("ai_unlocked_at")
    }
