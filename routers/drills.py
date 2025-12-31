"""Thinking drills routes for quick practice exercises.

Provides endpoints for:
- Creating new thinking drills (admin)
- Getting random drills (optionally filtered by type)
- Submitting drill answers
- Viewing drill history
- Getting drill statistics
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from database import get_database
from schemas.drill import (
    DrillCreate,
    DrillResponse,
    DrillSubmission,
    DrillResult,
    DrillType
)
from utils.auth import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter()


@router.post("", response_model=DrillResponse, status_code=status.HTTP_201_CREATED)
async def create_drill(
    drill: DrillCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new thinking drill (admin only in production)"""
    db = get_database()
    
    drill_data = {
        "title": drill.title,
        "drill_type": drill.drill_type,
        "question": drill.question,
        "options": drill.options,
        "correct_answer": drill.correct_answer,
        "explanation": drill.explanation,
        "created_at": datetime.utcnow()
    }
    
    result = await db.drills.insert_one(drill_data)
    drill_data["_id"] = result.inserted_id
    
    return {
        "id": str(drill_data["_id"]),
        "title": drill_data["title"],
        "drill_type": drill_data["drill_type"],
        "question": drill_data["question"],
        "options": drill_data["options"],
        "correct_answer": drill_data["correct_answer"],
        "explanation": drill_data["explanation"],
        "created_at": drill_data["created_at"]
    }


@router.get("/random")
async def get_random_drill(
    drill_type: DrillType = None,
    current_user: dict = Depends(get_current_user)
):
    """Get a random thinking drill that the user hasn't answered yet"""
    db = get_database()
    
    # Get all drill IDs that the user has already submitted
    submitted_drills = await db.drill_submissions.find(
        {"user_id": current_user["_id"]}
    ).to_list(length=None)
    
    submitted_drill_ids = [sub["drill_id"] for sub in submitted_drills]
    
    # Build query to exclude already-answered drills
    query = {"_id": {"$nin": submitted_drill_ids}}
    if drill_type:
        query["drill_type"] = drill_type
    
    # Use MongoDB aggregation for random selection
    pipeline = [{"$match": query}, {"$sample": {"size": 1}}]
    
    drills = await db.drills.aggregate(pipeline).to_list(length=None)
    
    if not drills:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No unanswered drills found. You've completed all available drills!"
        )
    
    drill = drills[0]
    
    # Don't return correct answer
    return {
        "id": str(drill["_id"]),
        "title": drill["title"],
        "drill_type": drill["drill_type"],
        "question": drill["question"],
        "options": drill["options"],
        "created_at": drill["created_at"]
    }


@router.post("/submit", response_model=DrillResult)
async def submit_drill(
    submission: DrillSubmission,
    current_user: dict = Depends(get_current_user)
):
    """Submit answer to a thinking drill"""
    db = get_database()
    
    # Get drill
    try:
        drill = await db.drills.find_one({"_id": ObjectId(submission.drill_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid drill ID"
        )
    
    if not drill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drill not found"
        )
    
    # Check answer
    is_correct = submission.user_answer.strip().lower() == drill["correct_answer"].strip().lower()
    
    # Save submission
    submission_data = {
        "user_id": current_user["_id"],
        "drill_id": ObjectId(submission.drill_id),
        "user_answer": submission.user_answer,
        "is_correct": is_correct,
        "submitted_at": datetime.utcnow()
    }
    
    await db.drill_submissions.insert_one(submission_data)
    
    return {
        "is_correct": is_correct,
        "explanation": drill["explanation"],
        "user_answer": submission.user_answer,
        "correct_answer": drill["correct_answer"]
    }


@router.get("/history")
async def get_drill_history(
    current_user: dict = Depends(get_current_user)
):
    """Get user's drill submission history"""
    db = get_database()
    
    submissions = await db.drill_submissions.find(
        {"user_id": current_user["_id"]}
    ).sort("submitted_at", -1).limit(50).to_list(length=None)
    
    # Get drill details for each submission
    results = []
    for sub in submissions:
        drill = await db.drills.find_one({"_id": sub["drill_id"]})
        if drill:
            results.append({
                "id": str(sub["_id"]),
                "drill_title": drill["title"],
                "drill_type": drill["drill_type"],
                "user_answer": sub["user_answer"],
                "is_correct": sub["is_correct"],
                "submitted_at": sub["submitted_at"]
            })
    
    return results


@router.get("/stats")
async def get_drill_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get user's drill statistics"""
    db = get_database()
    
    submissions = await db.drill_submissions.find({"user_id": current_user["_id"]}).to_list(length=None)
    
    if not submissions:
        return {
            "total_attempted": 0,
            "total_correct": 0,
            "accuracy": 0.0,
            "by_type": {}
        }
    
    total_attempted = len(submissions)
    total_correct = sum(1 for s in submissions if s["is_correct"])
    accuracy = (total_correct / total_attempted) * 100 if total_attempted > 0 else 0
    
    # Stats by drill type
    by_type = {}
    for sub in submissions:
        drill = await db.drills.find_one({"_id": sub["drill_id"]})
        if drill:
            drill_type = drill["drill_type"]
            if drill_type not in by_type:
                by_type[drill_type] = {"attempted": 0, "correct": 0}
            by_type[drill_type]["attempted"] += 1
            if sub["is_correct"]:
                by_type[drill_type]["correct"] += 1
    
    # Calculate accuracy for each type
    for drill_type in by_type:
        attempted = by_type[drill_type]["attempted"]
        correct = by_type[drill_type]["correct"]
        by_type[drill_type]["accuracy"] = (correct / attempted * 100) if attempted > 0 else 0
    
    return {
        "total_attempted": total_attempted,
        "total_correct": total_correct,
        "accuracy": round(accuracy, 2),
        "by_type": by_type
    }
