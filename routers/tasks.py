"""Task management routes.

Provides endpoints for:
- Creating new tasks (admin)
- Listing tasks with filters
- Getting specific task details
- Getting random tasks
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime
from database import get_database
from schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskFilter, Role, Difficulty
from utils.auth import get_current_user
from utils.admin import get_current_admin
from bson import ObjectId

router = APIRouter()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """Create a new engineering task.
    
    Admin-only endpoint to add new tasks to the platform.
    Tasks include scenario, prompts, difficulty level, and role.
    
    Args:
        task: Task details (title, description, role, difficulty, scenario, prompts)
        current_user: Injected current user from JWT token
    
    Returns:
        TaskResponse: Created task with generated ID
    """
    db = get_database()
    
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


@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    role: Optional[Role] = None,
    difficulty: Optional[Difficulty] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all tasks with optional filtering"""
    db = get_database()
    
    query = {}
    if role:
        query["role"] = role
    if difficulty:
        query["difficulty"] = difficulty
    
    tasks = await db.tasks.find(query).to_list(length=None)
    
    return [
        {
            "id": str(task["_id"]),
            "title": task["title"],
            "description": task["description"],
            "role": task["role"],
            "difficulty": task["difficulty"],
            "estimated_time_minutes": task["estimated_time_minutes"],
            "scenario": task["scenario"],
            "prompts": task["prompts"],
            "created_at": task["created_at"]
        }
        for task in tasks
    ]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific task by ID"""
    db = get_database()
    
    try:
        task = await db.tasks.find_one({"_id": ObjectId(task_id)})
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
    
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task["description"],
        "role": task["role"],
        "difficulty": task["difficulty"],
        "estimated_time_minutes": task["estimated_time_minutes"],
        "scenario": task["scenario"],
        "prompts": task["prompts"],
        "created_at": task["created_at"]
    }


@router.get("/random/pick")
async def get_random_task(
    role: Optional[Role] = None,
    difficulty: Optional[Difficulty] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get a random task matching filters"""
    db = get_database()
    
    query = {}
    if role:
        query["role"] = role
    if difficulty:
        query["difficulty"] = difficulty
    
    # Use MongoDB aggregation to get random task
    pipeline = [{"$match": query}]
    if query:
        pipeline.append({"$sample": {"size": 1}})
    else:
        pipeline = [{"$sample": {"size": 1}}]
    
    tasks = await db.tasks.aggregate(pipeline).to_list(length=None)
    
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tasks found matching criteria"
        )
    
    task = tasks[0]
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task["description"],
        "role": task["role"],
        "difficulty": task["difficulty"],
        "estimated_time_minutes": task["estimated_time_minutes"],
        "scenario": task["scenario"],
        "prompts": task["prompts"],
        "created_at": task["created_at"]
    }
