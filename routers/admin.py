"""Admin routes for task and drill management.

Provides endpoints for:
- Generating tasks with AI
- Generating drills with AI
- Creating tasks manually
- Creating drills manually
- Listing all tasks/drills
- Triggering daily task generation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from database import get_database
from schemas.task import TaskCreate, TaskResponse
from schemas.drill import DrillCreate, DrillResponse
from utils.admin import get_current_admin
from utils.ai_generation import generate_task_with_ai, generate_drill_with_ai, generate_daily_tasks
from datetime import datetime
from logger import get_logger
from utils.rate_limit import limiter

logger = get_logger(__name__)
router = APIRouter()


@router.post("/tasks/generate", response_model=TaskResponse)
@limiter.limit("5/minute")
async def generate_task(
    request: Request,
    role: str,
    difficulty: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Generate a task using AI and save it to database.
    
    Args:
        role: Engineering role (Backend Engineer, Frontend Engineer, etc.)
        difficulty: Task difficulty (beginner, intermediate, advanced)
        current_admin: Admin user (injected)
    
    Returns:
        TaskResponse: Generated and saved task
    """
    db = get_database()
    
    logger.info(f"Admin {current_admin['email']} generating task: {role}/{difficulty}")
    
    # Generate task with AI
    task_data = await generate_task_with_ai(role, difficulty)
    task_data["created_at"] = datetime.utcnow()
    
    # Save to database
    result = await db.tasks.insert_one(task_data)
    task_data["_id"] = result.inserted_id
    
    return {
        "id": str(task_data["_id"]),
        "title": task_data["title"],
        "description": task_data["description"],
        "role": task_data["role"],
        "difficulty": task_data["difficulty"],
        "estimated_time_minutes": task_data["estimated_time_minutes"],
        "scenario": task_data.get("scenario", ""),
        "prompts": task_data.get("prompts", []),
        "created_at": task_data["created_at"]
    }


@router.post("/drills/generate", response_model=DrillResponse)
@limiter.limit("5/minute")
async def generate_drill(
    request: Request,
    drill_type: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Generate a drill using AI and save it to database.
    
    Args:
        drill_type: Type of drill (spot_assumptions, rank_failures, etc.)
        current_admin: Admin user (injected)
    
    Returns:
        DrillResponse: Generated and saved drill
    """
    db = get_database()
    
    logger.info(f"Admin {current_admin['email']} generating drill: {drill_type}")
    
    # Generate drill with AI
    drill_data = await generate_drill_with_ai(drill_type)
    drill_data["created_at"] = datetime.utcnow()
    
    # Save to database
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


@router.post("/tasks/generate-daily")
@limiter.limit("2/minute")
async def generate_daily_tasks_endpoint(
    request: Request,
    current_admin: dict = Depends(get_current_admin)
):
    """Generate daily tasks for all roles using AI.
    
    This endpoint can be called manually or by cron job.
    
    Args:
        current_admin: Admin user (injected)
    
    Returns:
        dict: Summary of generated tasks
    """
    db = get_database()
    
    logger.info(f"Admin {current_admin['email']} triggered daily task generation")
    
    # Generate tasks
    tasks = await generate_daily_tasks()
    
    # Save to database
    inserted_ids = []
    for task_data in tasks:
        task_data["created_at"] = datetime.utcnow()
        result = await db.tasks.insert_one(task_data)
        inserted_ids.append(str(result.inserted_id))
    
    logger.info(f"Generated {len(inserted_ids)} daily tasks")
    
    return {
        "message": f"Successfully generated {len(tasks)} daily tasks",
        "task_ids": inserted_ids,
        "roles": [task["role"] for task in tasks]
    }


@router.post("/tasks/manual", response_model=TaskResponse)
async def create_task_manually(
    task: TaskCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """Create a task manually (without AI).
    
    Args:
        task: Task data
        current_admin: Admin user (injected)
    
    Returns:
        TaskResponse: Created task
    """
    db = get_database()
    
    logger.info(f"Admin {current_admin['email']} creating manual task: {task.title}")
    
    task_data = {
        "title": task.title,
        "description": task.description,
        "role": task.role,
        "difficulty": task.difficulty,
        "estimated_time_minutes": task.estimated_time_minutes,
        "scenario": task.scenario,
        "prompts": task.prompts,
        "created_at": datetime.utcnow()
    }
    
    result = await db.tasks.insert_one(task_data)
    task_data["_id"] = result.inserted_id
    
    return {
        "id": str(task_data["_id"]),
        "title": task_data["title"],
        "description": task_data["description"],
        "role": task_data["role"],
        "difficulty": task_data["difficulty"],
        "estimated_time_minutes": task_data["estimated_time_minutes"],
        "scenario": task_data["scenario"],
        "prompts": task_data["prompts"],
        "created_at": task_data["created_at"]
    }


@router.post("/drills/manual", response_model=DrillResponse)
async def create_drill_manually(
    drill: DrillCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """Create a drill manually (without AI).
    
    Args:
        drill: Drill data
        current_admin: Admin user (injected)
    
    Returns:
        DrillResponse: Created drill
    """
    db = get_database()
    
    logger.info(f"Admin {current_admin['email']} creating manual drill: {drill.title}")
    
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


@router.get("/stats")
@limiter.limit("30/minute")
async def get_admin_stats(request: Request, current_admin: dict = Depends(get_current_admin)):
    """Get admin statistics.
    
    Args:
        current_admin: Admin user (injected)
    
    Returns:
        dict: Platform statistics
    """
    db = get_database()
    
    total_users = await db.users.count_documents({})
    total_tasks = await db.tasks.count_documents({})
    total_drills = await db.drills.count_documents({})
    total_responses = await db.responses.count_documents({})
    
    return {
        "total_users": total_users,
        "total_tasks": total_tasks,
        "total_drills": total_drills,
        "total_responses": total_responses
    }
