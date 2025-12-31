"""Cron job scheduler for automated tasks using fastapi_crons.

Runs scheduled jobs:
- Daily task generation at midnight
"""

from database import get_database
from utils.ai_generation import generate_daily_tasks
from logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

# Crons instance will be initialized in main.py
# This function will be decorated there

async def daily_task_generation_job():
    """Job that runs at midnight to generate daily tasks for all roles."""
    logger.info("Starting daily task generation job")
    
    try:
        db = get_database()
        
        # Generate tasks
        tasks = await generate_daily_tasks()
        
        # Save to database
        inserted_count = 0
        for task_data in tasks:
            task_data["created_at"] = datetime.utcnow()
            await db.tasks.insert_one(task_data)
            inserted_count += 1
        
        logger.info(f"Daily task generation completed: {inserted_count} tasks created")
        return f"Successfully generated {inserted_count} tasks"
        
    except Exception as e:
        logger.error(f"Error in daily task generation job: {str(e)}")
        return f"Error: {str(e)}"
