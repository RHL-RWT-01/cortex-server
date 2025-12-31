from fastapi import APIRouter, HTTPException, status, Depends
from database import get_database
from schemas.user import UserUpdate, UserResponse
from utils.auth import get_current_user

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get authenticated user's profile information.
    
    Returns complete profile including email, name, role, and activity dates.
    
    Args:
        current_user: Injected current user from JWT token
    
    Returns:
        UserResponse: User profile data
    """
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "selected_role": current_user.get("selected_role"),
        "created_at": current_user["created_at"],
        "last_login": current_user.get("last_login")
    }


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile information.
    
    Allows updating full name and selected role.
    Only provided fields will be updated.
    
    Args:
        user_update: Fields to update (full_name, selected_role)
        current_user: Injected current user from JWT token
    
    Returns:
        UserResponse: Updated user profile
    
    Raises:
        HTTPException 400: If no fields provided to update
    """
    db = get_database()
    
    update_data = {}
    if user_update.full_name is not None:
        update_data["full_name"] = user_update.full_name
    if user_update.selected_role is not None:
        update_data["selected_role"] = user_update.selected_role
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_data}
    )
    
    # Get updated user
    updated_user = await db.users.find_one({"_id": current_user["_id"]})
    
    return {
        "id": str(updated_user["_id"]),
        "email": updated_user["email"],
        "full_name": updated_user["full_name"],
        "selected_role": updated_user.get("selected_role"),
        "created_at": updated_user["created_at"],
        "last_login": updated_user.get("last_login")
    }
