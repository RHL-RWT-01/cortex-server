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


@router.get("/tasks")
async def get_all_tasks(current_admin: dict = Depends(get_current_admin)):
    """Get all tasks for admin management.
    
    Args:
        current_admin: Admin user (injected)
    
    Returns:
        List[dict]: All tasks
    """
    db = get_database()
    
    tasks = await db.tasks.find({}).sort("created_at", -1).to_list(length=None)
    
    return [
        {
            "id": str(task["_id"]),
            "title": task["title"],
            "description": task["description"],
            "role": task["role"],
            "difficulty": task["difficulty"],
            "estimated_time_minutes": task["estimated_time_minutes"],
            "scenario": task.get("scenario", ""),
            "prompts": task.get("prompts", []),
            "created_at": task["created_at"]
        }
        for task in tasks
    ]


@router.get("/drills")
async def get_all_drills(current_admin: dict = Depends(get_current_admin)):
    """Get all drills for admin management.
    
    Args:
        current_admin: Admin user (injected)
    
    Returns:
        List[dict]: All drills
    """
    db = get_database()
    
    drills = await db.drills.find({}).sort("created_at", -1).to_list(length=None)
    
    return [
        {
            "id": str(drill["_id"]),
            "title": drill["title"],
            "drill_type": drill["drill_type"],
            "question": drill["question"],
            "options": drill["options"],
            "correct_answer": drill["correct_answer"],
            "explanation": drill["explanation"],
            "created_at": drill["created_at"]
        }
        for drill in drills
    ]


@router.put("/tasks/{task_id}")
async def update_task(
    task_id: str,
    task: TaskCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """Update a task by ID.
    
    Args:
        task_id: Task ID to update
        task: Updated task data
        current_admin: Admin user (injected)
    
    Returns:
        dict: Success message
    """
    from bson import ObjectId
    db = get_database()
    
    try:
        task_data = {
            "title": task.title,
            "description": task.description,
            "role": task.role,
            "difficulty": task.difficulty,
            "estimated_time_minutes": task.estimated_time_minutes,
            "scenario": task.scenario,
            "prompts": task.prompts
        }
        
        result = await db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": task_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        logger.info(f"Admin {current_admin['email']} updated task {task_id}")
        
        return {"message": "Task updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID or data"
        )


@router.put("/drills/{drill_id}")
async def update_drill(
    drill_id: str,
    drill: DrillCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """Update a drill by ID.
    
    Args:
        drill_id: Drill ID to update
        drill: Updated drill data
        current_admin: Admin user (injected)
    
    Returns:
        dict: Success message
    """
    from bson import ObjectId
    db = get_database()
    
    try:
        drill_data = {
            "title": drill.title,
            "drill_type": drill.drill_type,
            "question": drill.question,
            "options": drill.options,
            "correct_answer": drill.correct_answer,
            "explanation": drill.explanation
        }
        
        result = await db.drills.update_one(
            {"_id": ObjectId(drill_id)},
            {"$set": drill_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Drill not found"
            )
        
        logger.info(f"Admin {current_admin['email']} updated drill {drill_id}")
        
        return {"message": "Drill updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update drill {drill_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid drill ID or data"
        )


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, current_admin: dict = Depends(get_current_admin)):
    """Delete a task by ID.
    
    Args:
        task_id: Task ID to delete
        current_admin: Admin user (injected)
    
    Returns:
        dict: Success message
    """
    from bson import ObjectId
    db = get_database()
    
    try:
        result = await db.tasks.delete_one({"_id": ObjectId(task_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        logger.info(f"Admin {current_admin['email']} deleted task {task_id}")
        
        return {"message": "Task deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID"
        )


@router.delete("/drills/{drill_id}")
async def delete_drill(drill_id: str, current_admin: dict = Depends(get_current_admin)):
    """Delete a drill by ID.
    
    Args:
        drill_id: Drill ID to delete
        current_admin: Admin user (injected)
    
    Returns:
        dict: Success message
    """
    from bson import ObjectId
    db = get_database()
    
    try:
        result = await db.drills.delete_one({"_id": ObjectId(drill_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Drill not found"
            )
        
        logger.info(f"Admin {current_admin['email']} deleted drill {drill_id}")
        
        return {"message": "Drill deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete drill {drill_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid drill ID"
        )
