"""Subscription management routes.

Provides endpoints for:
- Getting current subscription status
- Creating checkout sessions for upgrades
- Getting usage limits
- Cancelling subscriptions
- Accessing customer portal
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from datetime import datetime
from database import get_database
from schemas.subscription import (
    SubscriptionResponse,
    CreateCheckoutRequest,
    CheckoutResponse,
    UsageLimitsResponse,
    CancelSubscriptionResponse,
    CustomerPortalResponse
)
from utils.auth import get_current_user
from utils.subscription import get_user_subscription, get_usage_stats
from utils.rate_limit import limiter
from config import settings
from logger import get_logger
import dodopayments

logger = get_logger(__name__)

router = APIRouter()

# Initialize DodoPayments client
def get_dodo_client():
    """Get configured DodoPayments client."""
    if not settings.dodo_payments_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service not configured"
        )
    return dodopayments.DodoPayments(bearer_token=settings.dodo_payments_api_key)


@router.get("/me", response_model=SubscriptionResponse)
@limiter.limit("30/minute")
async def get_subscription(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get current user's subscription status."""
    subscription = await get_user_subscription(current_user["_id"])
    
    if not subscription:
        return {
            "plan": "free",
            "status": "active",
            "current_period_end": None
        }
    
    return {
        "plan": subscription.get("plan", "free"),
        "status": subscription.get("status", "active"),
        "current_period_end": subscription.get("current_period_end")
    }


@router.get("/usage", response_model=UsageLimitsResponse)
@limiter.limit("60/minute")
async def get_usage(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get current usage statistics and limits."""
    usage = await get_usage_stats(current_user["_id"])
    return usage


@router.post("/checkout", response_model=CheckoutResponse)
@limiter.limit("10/minute")
async def create_checkout(
    request: Request,
    checkout_request: CreateCheckoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a checkout session for Pro subscription.
    
    Optionally accepts a discount_code for promotional pricing.
    """
    if not settings.dodo_product_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment product not configured"
        )
    
    try:
        client = get_dodo_client()
        
        # Build payment request
        payment_data = {
            "billing": {
                "city": "N/A",
                "country": "IN",
                "state": "N/A",
                "street": "N/A",
                "zipcode": "00000"
            },
            "customer": {
                "email": current_user["email"],
                "name": current_user.get("full_name", current_user["email"])
            },
            "product_id": settings.dodo_product_id,
            "quantity": 1,
            "payment_link": True,
            "metadata": {
                "user_id": str(current_user["_id"]),
                "user_email": current_user["email"]
            }
        }
        
        # Add discount code if provided
        if checkout_request.discount_code:
            payment_data["discount_code"] = checkout_request.discount_code
        
        # Add redirect URLs if provided
        if checkout_request.success_url:
            payment_data["return_url"] = checkout_request.success_url
        
        # Create subscription via DodoPayments
        response = client.subscriptions.create(**payment_data)
        
        logger.info(f"Checkout created for user {current_user['email']}: {response.subscription_id}")
        
        return {
            "checkout_url": response.payment_link or response.customer.customer_id,
            "payment_link": response.payment_link or ""
        }
        
    except Exception as e:
        logger.error(f"Failed to create checkout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )


@router.post("/cancel", response_model=CancelSubscriptionResponse)
@limiter.limit("5/minute")
async def cancel_subscription(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Cancel user's Pro subscription."""
    subscription = await get_user_subscription(current_user["_id"])
    
    if not subscription or subscription.get("plan") == "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to cancel"
        )
    
    if not subscription.get("subscription_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No subscription ID found"
        )
    
    try:
        client = get_dodo_client()
        
        # Cancel subscription via DodoPayments
        client.subscriptions.update(
            subscription_id=subscription["subscription_id"],
            status="cancelled"
        )
        
        # Update local subscription status
        db = get_database()
        await db.subscriptions.update_one(
            {"user_id": current_user["_id"]},
            {
                "$set": {
                    "status": "cancelled",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Subscription cancelled for user {current_user['email']}")
        
        return {
            "message": "Subscription cancelled successfully. You'll retain access until the end of your billing period.",
            "cancelled_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.get("/portal", response_model=CustomerPortalResponse)
@limiter.limit("10/minute")
async def get_customer_portal(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get URL to customer portal for managing subscription."""
    subscription = await get_user_subscription(current_user["_id"])
    
    if not subscription or not subscription.get("customer_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No subscription found. Subscribe first to access the customer portal."
        )
    
    try:
        client = get_dodo_client()
        
        # Get customer portal URL
        response = client.customers.get_customer_portal(
            customer_id=subscription["customer_id"]
        )
        
        return {
            "portal_url": response.link
        }
        
    except Exception as e:
        logger.error(f"Failed to get customer portal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to access customer portal: {str(e)}"
        )
