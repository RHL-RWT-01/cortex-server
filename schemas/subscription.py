"""Subscription schemas for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class SubscriptionResponse(BaseModel):
    """User-facing subscription information."""
    plan: Literal["free", "pro"]
    status: Literal["active", "cancelled", "on_hold", "expired"]
    current_period_end: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CreateCheckoutRequest(BaseModel):
    """Request to create a checkout session."""
    discount_code: Optional[str] = Field(None, description="Optional coupon/discount code")
    success_url: Optional[str] = Field(None, description="URL to redirect after successful payment")
    cancel_url: Optional[str] = Field(None, description="URL to redirect if payment is cancelled")


class CheckoutResponse(BaseModel):
    """Response with checkout URL."""
    checkout_url: str
    payment_link: str


class UsageLimitsResponse(BaseModel):
    """Current usage vs limits for the user."""
    plan: Literal["free", "pro"]
    
    # Task limits
    tasks_used: int = Field(description="Tasks completed (lifetime for free, today for pro)")
    tasks_limit: int = Field(description="Maximum tasks allowed")
    can_submit_task: bool
    
    # Drill limits
    drills_used_today: int
    drills_limit: int = Field(description="Maximum drills per day")
    can_submit_drill: bool


class CancelSubscriptionResponse(BaseModel):
    """Response for subscription cancellation."""
    message: str
    cancelled_at: datetime


class CustomerPortalResponse(BaseModel):
    """Response with customer portal URL."""
    portal_url: str
