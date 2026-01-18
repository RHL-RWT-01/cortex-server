"""Webhook handlers for external payment events.

Handles incoming webhooks from DodoPayments for:
- Subscription activation
- Subscription cancellation
- Subscription renewal
- Payment events
"""

from fastapi import APIRouter, HTTPException, status, Request, Header
from datetime import datetime
from database import get_database
from utils.subscription import create_or_update_subscription
from config import settings
from logger import get_logger
from bson import ObjectId
import hmac
import hashlib

logger = get_logger(__name__)

router = APIRouter()


def verify_webhook_signature(
    payload: bytes, 
    webhook_id: str,
    webhook_timestamp: str,
    webhook_signature: str, 
    secret: str
) -> bool:
    """Verify DodoPayments webhook signature using Standard Webhooks format.
    
    DodoPayments uses the Standard Webhooks spec:
    - Signed message = {webhook-id}.{webhook-timestamp}.{payload}
    - HMAC SHA256 with base64-encoded secret
    - Signature header may contain multiple signatures (v1,xxx v1,yyy)
    
    Args:
        payload: Raw request body bytes
        webhook_id: webhook-id header value
        webhook_timestamp: webhook-timestamp header value  
        webhook_signature: webhook-signature header value
        secret: Webhook secret key (may be prefixed with 'whsec_')
        
    Returns:
        True if signature is valid
    """
    import base64
    
    if not secret:
        logger.warning("Webhook secret not configured, skipping verification")
        return True
    
    # Remove 'whsec_' prefix if present
    if secret.startswith("whsec_"):
        secret = secret[6:]
    
    # Decode the base64 secret
    try:
        secret_bytes = base64.b64decode(secret)
    except Exception:
        # If not base64, use as-is
        secret_bytes = secret.encode()
    
    # Build the signed message: {id}.{timestamp}.{payload}
    signed_payload = f"{webhook_id}.{webhook_timestamp}.{payload.decode('utf-8')}"
    
    # Compute expected signature
    expected_signature = hmac.new(
        secret_bytes,
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).digest()
    expected_signature_b64 = base64.b64encode(expected_signature).decode('utf-8')
    
    # The header may have multiple signatures like "v1,xxx v1,yyy"
    # We need to check if any matches
    for sig_part in webhook_signature.split(" "):
        if "," in sig_part:
            version, sig = sig_part.split(",", 1)
            if version == "v1":
                if hmac.compare_digest(sig, expected_signature_b64):
                    return True
        else:
            # Fallback: compare directly
            if hmac.compare_digest(sig_part, expected_signature_b64):
                return True
    
    return False


async def handle_subscription_active(data: dict):
    """Handle subscription.active webhook event."""
    subscription_id = data.get("subscription_id")
    customer = data.get("customer", {})
    customer_id = customer.get("customer_id")
    customer_email = customer.get("email")
    
    # Get user_id from metadata
    metadata = data.get("metadata", {})
    user_id_str = metadata.get("user_id")
    
    if not user_id_str:
        # Try to find user by email
        db = get_database()
        user = await db.users.find_one({"email": customer_email})
        if user:
            user_id_str = str(user["_id"])
        else:
            logger.error(f"Cannot find user for subscription {subscription_id}")
            return
    
    user_id = ObjectId(user_id_str)
    
    # Parse period dates if available
    current_period_start = None
    current_period_end = None
    
    if data.get("current_period_start"):
        try:
            current_period_start = datetime.fromisoformat(data["current_period_start"].replace("Z", "+00:00"))
        except:
            pass
    
    if data.get("current_period_end"):
        try:
            current_period_end = datetime.fromisoformat(data["current_period_end"].replace("Z", "+00:00"))
        except:
            pass
    
    await create_or_update_subscription(
        user_id=user_id,
        plan="pro",
        status="active",
        subscription_id=subscription_id,
        customer_id=customer_id,
        current_period_start=current_period_start,
        current_period_end=current_period_end
    )
    
    logger.info(f"Subscription activated for user {user_id}: {subscription_id}")


async def handle_subscription_cancelled(data: dict):
    """Handle subscription.cancelled webhook event."""
    subscription_id = data.get("subscription_id")
    
    db = get_database()
    
    # Find subscription by subscription_id
    subscription = await db.subscriptions.find_one({"subscription_id": subscription_id})
    
    if not subscription:
        logger.warning(f"Subscription not found for cancellation: {subscription_id}")
        return
    
    await db.subscriptions.update_one(
        {"subscription_id": subscription_id},
        {
            "$set": {
                "status": "cancelled",
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    logger.info(f"Subscription cancelled: {subscription_id}")


async def handle_subscription_on_hold(data: dict):
    """Handle subscription.on_hold webhook event (failed renewal)."""
    subscription_id = data.get("subscription_id")
    
    db = get_database()
    
    await db.subscriptions.update_one(
        {"subscription_id": subscription_id},
        {
            "$set": {
                "status": "on_hold",
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    logger.warning(f"Subscription on hold (payment failed): {subscription_id}")


async def handle_subscription_renewed(data: dict):
    """Handle subscription.renewed webhook event."""
    subscription_id = data.get("subscription_id")
    
    db = get_database()
    
    # Parse new period dates
    current_period_start = None
    current_period_end = None
    
    if data.get("current_period_start"):
        try:
            current_period_start = datetime.fromisoformat(data["current_period_start"].replace("Z", "+00:00"))
        except:
            pass
    
    if data.get("current_period_end"):
        try:
            current_period_end = datetime.fromisoformat(data["current_period_end"].replace("Z", "+00:00"))
        except:
            pass
    
    update_data = {
        "status": "active",
        "updated_at": datetime.utcnow()
    }
    
    if current_period_start:
        update_data["current_period_start"] = current_period_start
    if current_period_end:
        update_data["current_period_end"] = current_period_end
    
    await db.subscriptions.update_one(
        {"subscription_id": subscription_id},
        {"$set": update_data}
    )
    
    logger.info(f"Subscription renewed: {subscription_id}")


async def handle_subscription_expired(data: dict):
    """Handle subscription.expired webhook event."""
    subscription_id = data.get("subscription_id")
    
    db = get_database()
    
    await db.subscriptions.update_one(
        {"subscription_id": subscription_id},
        {
            "$set": {
                "status": "expired",
                "plan": "free",  # Downgrade to free
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    logger.info(f"Subscription expired, downgraded to free: {subscription_id}")


# Event handler mapping
EVENT_HANDLERS = {
    "subscription.active": handle_subscription_active,
    "subscription.cancelled": handle_subscription_cancelled,
    "subscription.on_hold": handle_subscription_on_hold,
    "subscription.renewed": handle_subscription_renewed,
    "subscription.expired": handle_subscription_expired,
}


@router.post("/dodo")
async def dodo_webhook(
    request: Request,
    webhook_id: str = Header(None, alias="webhook-id"),
    webhook_signature: str = Header(None, alias="webhook-signature"),
    webhook_timestamp: str = Header(None, alias="webhook-timestamp")
):
    """Handle incoming DodoPayments webhook events.
    
    Verifies signature using Standard Webhooks format and processes subscription lifecycle events.
    """
    # Get raw body for signature verification
    body = await request.body()
    
    # Verify signature
    if settings.dodo_webhook_secret:
        if not webhook_signature or not webhook_id or not webhook_timestamp:
            logger.warning(f"Webhook received with missing headers: id={webhook_id}, sig={bool(webhook_signature)}, ts={webhook_timestamp}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing webhook headers (webhook-id, webhook-signature, or webhook-timestamp)"
            )
        
        if not verify_webhook_signature(body, webhook_id, webhook_timestamp, webhook_signature, settings.dodo_webhook_secret):
            logger.warning("Invalid webhook signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
    
    # Parse JSON body
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse webhook payload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    
    # Get event type
    event_type = payload.get("type") or payload.get("event_type")
    
    if not event_type:
        logger.warning(f"Webhook received without event type: {payload}")
        return {"status": "ignored", "reason": "no event type"}
    
    logger.info(f"Webhook received: {event_type}")
    
    # Get event data
    data = payload.get("data", payload)
    
    # Handle event
    handler = EVENT_HANDLERS.get(event_type)
    
    if handler:
        try:
            await handler(data)
            return {"status": "processed", "event": event_type}
        except Exception as e:
            logger.error(f"Failed to handle webhook {event_type}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process webhook: {str(e)}"
            )
    else:
        logger.info(f"Unhandled webhook event: {event_type}")
        return {"status": "ignored", "event": event_type}
