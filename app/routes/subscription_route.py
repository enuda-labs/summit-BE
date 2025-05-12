from fastapi import APIRouter, HTTPException
from app.models.user import User, User_Pydantic, UserIn_Pydantic, UserRegister
from typing import List
from app.services import sub_process as subscription_service
from fastapi import Request

router = APIRouter()

@router.post("/create-subscription/{user_id}/{plan}/{frequency}")
async def create_subscription(user_id: int, plan: str, frequency: str = "monthly"):
    return await subscription_service.create_subscription(user_id, plan, frequency)


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    return await subscription_service.stripe_webhook(request)


@router.get("/get-subscription-by-user-id/{user_id}")
async def get_subscription_by_user_id(user_id: int):
    return await subscription_service.get_subscription_by_user_id(user_id)