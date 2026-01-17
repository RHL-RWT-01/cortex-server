"""Subscription utility functions.

Provides helper functions for subscription management and usage limit checks.
"""

from datetime import datetime, timedelta
from typing import Tuple, Optional
from bson import ObjectId
from database import get_database
from logger import get_logger

logger = get_logger(__name__)

# Plan limits configuration
PLAN_LIMITS = {
    "free": {
        "tasks_total": 1,      # 1 task lifetime (not per day)
        "tasks_per_day": None,  # Not applicable for free (lifetime limit)
        "drills_per_day": 1,
    },
    "pro": {
        "tasks_total": None,    # Unlimited lifetime
        "tasks_per_day": 5,     # 5 per day
        "drills_per_day": None,  # Unlimited
    }
}


async def get_user_subscription(user_id: ObjectId) -> Optional[dict]:
    """Get user's subscription record.
    
    Args:
        user_id: User's ObjectId
        
    Returns:
        Subscription dict or None if no subscription exists
    """
    db = get_database()
    subscription = await db.subscriptions.find_one({"user_id": user_id})
    return subscription


async def get_user_plan(user_id: ObjectId) -> str:
    """Get user's current plan.
    
    Args:
        user_id: User's ObjectId
        
    Returns:
        "free" or "pro"
    """
    subscription = await get_user_subscription(user_id)
    
    if not subscription:
        return "free"
    
    # Check if subscription is active
    if subscription.get("status") != "active":
        return "free"
    
    return subscription.get("plan", "free")


async def get_tasks_count_lifetime(user_id: ObjectId) -> int:
    """Get total number of tasks completed by user (lifetime).
    
    Args:
        user_id: User's ObjectId
        
    Returns:
        Number of tasks completed ever
    """
    db = get_database()
    count = await db.responses.count_documents({"user_id": user_id})
    return count


async def get_tasks_count_today(user_id: ObjectId) -> int:
    """Get number of tasks completed by user today.
    
    Args:
        user_id: User's ObjectId
        
    Returns:
        Number of tasks completed today
    """
    db = get_database()
    
    # Get start of today (UTC)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    count = await db.responses.count_documents({
        "user_id": user_id,
        "submitted_at": {"$gte": today_start}
    })
    return count


async def get_drills_count_today(user_id: ObjectId) -> int:
    """Get number of drills completed by user today.
    
    Args:
        user_id: User's ObjectId
        
    Returns:
        Number of drills completed today
    """
    db = get_database()
    
    # Get start of today (UTC)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    count = await db.drill_submissions.count_documents({
        "user_id": user_id,
        "submitted_at": {"$gte": today_start}
    })
    return count


async def check_task_limit(user_id: ObjectId) -> Tuple[bool, str]:
    """Check if user can submit a task based on their plan limits.
    
    Args:
        user_id: User's ObjectId
        
    Returns:
        Tuple of (can_submit: bool, reason: str)
    """
    plan = await get_user_plan(user_id)
    limits = PLAN_LIMITS[plan]
    
    if plan == "free":
        # Free tier: 1 task lifetime
        tasks_used = await get_tasks_count_lifetime(user_id)
        if tasks_used >= limits["tasks_total"]:
            return False, "You've used your free task. Upgrade to Pro for 5 tasks per day!"
        return True, ""
    
    else:  # Pro
        # Pro tier: 5 tasks per day
        tasks_today = await get_tasks_count_today(user_id)
        if limits["tasks_per_day"] and tasks_today >= limits["tasks_per_day"]:
            return False, f"You've reached your daily limit of {limits['tasks_per_day']} tasks. Come back tomorrow!"
        return True, ""


async def check_drill_limit(user_id: ObjectId) -> Tuple[bool, str]:
    """Check if user can submit a drill based on their plan limits.
    
    Args:
        user_id: User's ObjectId
        
    Returns:
        Tuple of (can_submit: bool, reason: str)
    """
    plan = await get_user_plan(user_id)
    limits = PLAN_LIMITS[plan]
    
    if plan == "free":
        # Free tier: 1 drill per day
        drills_today = await get_drills_count_today(user_id)
        if drills_today >= limits["drills_per_day"]:
            return False, "You've used your daily free drill. Upgrade to Pro for unlimited drills!"
        return True, ""
    
    else:  # Pro - unlimited drills
        return True, ""


async def get_usage_stats(user_id: ObjectId) -> dict:
    """Get comprehensive usage statistics for a user.
    
    Args:
        user_id: User's ObjectId
        
    Returns:
        Dict with usage stats and limits
    """
    plan = await get_user_plan(user_id)
    limits = PLAN_LIMITS[plan]
    
    tasks_lifetime = await get_tasks_count_lifetime(user_id)
    tasks_today = await get_tasks_count_today(user_id)
    drills_today = await get_drills_count_today(user_id)
    
    can_submit_task, _ = await check_task_limit(user_id)
    can_submit_drill, _ = await check_drill_limit(user_id)
    
    if plan == "free":
        tasks_used = tasks_lifetime
        tasks_limit = limits["tasks_total"]
    else:
        tasks_used = tasks_today
        tasks_limit = limits["tasks_per_day"] or -1  # -1 = unlimited
    
    drills_limit = limits["drills_per_day"] if limits["drills_per_day"] else -1  # -1 = unlimited
    
    return {
        "plan": plan,
        "tasks_used": tasks_used,
        "tasks_limit": tasks_limit,
        "can_submit_task": can_submit_task,
        "drills_used_today": drills_today,
        "drills_limit": drills_limit,
        "can_submit_drill": can_submit_drill
    }


async def create_or_update_subscription(
    user_id: ObjectId,
    plan: str,
    status: str,
    subscription_id: str = None,
    customer_id: str = None,
    current_period_start: datetime = None,
    current_period_end: datetime = None
) -> dict:
    """Create or update a user's subscription.
    
    Args:
        user_id: User's ObjectId
        plan: "free" or "pro"
        status: Subscription status
        subscription_id: DodoPayments subscription ID
        customer_id: DodoPayments customer ID
        current_period_start: Start of billing period
        current_period_end: End of billing period
        
    Returns:
        Updated subscription document
    """
    db = get_database()
    
    now = datetime.utcnow()
    
    subscription_data = {
        "user_id": user_id,
        "plan": plan,
        "status": status,
        "subscription_id": subscription_id,
        "customer_id": customer_id,
        "current_period_start": current_period_start,
        "current_period_end": current_period_end,
        "updated_at": now
    }
    
    # Upsert - update if exists, create if not
    result = await db.subscriptions.update_one(
        {"user_id": user_id},
        {
            "$set": subscription_data,
            "$setOnInsert": {"created_at": now}
        },
        upsert=True
    )
    
    logger.info(f"Subscription updated for user {user_id}: plan={plan}, status={status}")
    
    return await db.subscriptions.find_one({"user_id": user_id})
