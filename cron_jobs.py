"""Cron job scheduler for automated tasks using fastapi_crons.

Runs scheduled jobs:
- Daily task generation at midnight (generates 21 tasks: 7 roles x 3 difficulties)
"""

from database import get_database
from utils.ai_generation import generate_daily_tasks
from logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

# Crons instance will be initialized in main.py
# This function will be decorated there

async def daily_task_generation_job():
    """Job that runs at midnight to generate daily tasks for all roles and difficulties.
    
    Generates 21 tasks total (7 roles x 3 difficulties) with deduplication.
    """
    logger.cron("=" * 60)
    logger.cron("CRON JOB STARTED: daily_task_generation")
    logger.cron(f"Execution time (UTC): {datetime.utcnow().isoformat()}")
    
    try:
        db = get_database()
        
        # Generate tasks with database for deduplication
        logger.cron("Generating tasks for all roles and difficulties...")
        tasks = await generate_daily_tasks(db=db)
        
        if not tasks:
            logger.cron("WARNING: No tasks were generated!")
            logger.cron("CRON JOB COMPLETED: daily_task_generation (0 tasks)")
            logger.cron("=" * 60)
            return "No tasks generated"
        
        # Save to database
        inserted_count = 0
        for task_data in tasks:
            task_data["created_at"] = datetime.utcnow()
            result = await db.tasks.insert_one(task_data)
            inserted_count += 1
            logger.cron(f"Inserted: {task_data['role']} / {task_data['difficulty']} - {task_data['title'][:50]}...")
        
        logger.cron(f"CRON JOB COMPLETED: daily_task_generation")
        logger.cron(f"Total tasks created: {inserted_count}")
        logger.cron("=" * 60)
        return f"Successfully generated {inserted_count} tasks"
        
    except Exception as e:
        logger.cron(f"CRON JOB FAILED: daily_task_generation")
        logger.cron(f"Error: {str(e)}")
        import traceback
        logger.error(f"Cron job traceback: {traceback.format_exc()}")
        logger.cron("=" * 60)
        return f"Error: {str(e)}"

