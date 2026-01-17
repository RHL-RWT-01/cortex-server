"""Subscription model for SaaS billing.

Stores user subscription data from DodoPayments.
"""

from datetime import datetime
from typing import Optional
from bson import ObjectId


class Subscription:
    """MongoDB model for user subscriptions."""
    
    collection_name = "subscriptions"
    
    def __init__(
        self,
        user_id: ObjectId,
        plan: str = "free",  # "free" or "pro"
        status: str = "active",  # active, cancelled, on_hold, expired
        subscription_id: Optional[str] = None,  # DodoPayments subscription ID
        customer_id: Optional[str] = None,  # DodoPayments customer ID
        current_period_start: Optional[datetime] = None,
        current_period_end: Optional[datetime] = None,
        created_at: datetime = None,
        updated_at: datetime = None,
        _id: ObjectId = None
    ):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.plan = plan
        self.status = status
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.current_period_start = current_period_start
        self.current_period_end = current_period_end
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self):
        return {
            "_id": self._id,
            "user_id": self.user_id,
            "plan": self.plan,
            "status": self.status,
            "subscription_id": self.subscription_id,
            "customer_id": self.customer_id,
            "current_period_start": self.current_period_start,
            "current_period_end": self.current_period_end,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @staticmethod
    def from_dict(data: dict):
        return Subscription(
            _id=data.get("_id"),
            user_id=data["user_id"],
            plan=data.get("plan", "free"),
            status=data.get("status", "active"),
            subscription_id=data.get("subscription_id"),
            customer_id=data.get("customer_id"),
            current_period_start=data.get("current_period_start"),
            current_period_end=data.get("current_period_end"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
