from datetime import datetime
from typing import Optional
from bson import ObjectId


class User:
    collection_name = "users"
    
    def __init__(
        self,
        email: str,
        hashed_password: str,
        full_name: str,
        selected_role: Optional[str] = None,
        selected_level: Optional[str] = None,
        subscription_plan: str = "free",  # "free" or "pro"
        dodo_customer_id: Optional[str] = None,  # DodoPayments customer ID
        created_at: datetime = None,
        last_login: Optional[datetime] = None,
        _id: ObjectId = None
    ):
        self._id = _id or ObjectId()
        self.email = email
        self.hashed_password = hashed_password
        self.full_name = full_name
        self.selected_role = selected_role
        self.selected_level = selected_level
        self.subscription_plan = subscription_plan
        self.dodo_customer_id = dodo_customer_id
        self.created_at = created_at or datetime.utcnow()
        self.last_login = last_login
    
    def to_dict(self):
        return {
            "_id": self._id,
            "email": self.email,
            "hashed_password": self.hashed_password,
            "full_name": self.full_name,
            "selected_role": self.selected_role,
            "selected_level": self.selected_level,
            "subscription_plan": self.subscription_plan,
            "dodo_customer_id": self.dodo_customer_id,
            "created_at": self.created_at,
            "last_login": self.last_login
        }
    
    @staticmethod
    def from_dict(data: dict):
        return User(
            _id=data.get("_id"),
            email=data["email"],
            hashed_password=data["hashed_password"],
            full_name=data["full_name"],
            selected_role=data.get("selected_role"),
            selected_level=data.get("selected_level"),
            subscription_plan=data.get("subscription_plan", "free"),
            dodo_customer_id=data.get("dodo_customer_id"),
            created_at=data.get("created_at"),
            last_login=data.get("last_login")
        )
