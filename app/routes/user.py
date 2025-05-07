from fastapi import APIRouter, HTTPException
from app.models.user import User, User_Pydantic, UserIn_Pydantic, UserRegister
from typing import List
from app.services import user as user_service

router = APIRouter()

@router.post("/register", response_model=User_Pydantic)
async def register_user(user: UserRegister):
    try:
        return await user_service.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/all/users", response_model=List[User_Pydantic])
async def get_all_users():
    return await user_service.get_all_users()

@router.get("/users/{user_id}", response_model=User_Pydantic)
async def read_user(user_id: int):
    return await user_service.get_user(user_id=user_id)

@router.put("/users/{user_id}", response_model=User_Pydantic)
async def update_user_details(user_id: int, user: UserIn_Pydantic):
    return await user_service.update_user(user_id=user_id, user=user)

@router.delete("/users/{user_email}", response_model=User_Pydantic)
async def delete_user(user_email: str):
    return await user_service.delete_user(user_email=user_email)

@router.post("/verify-otp/{otp}/{recipient_email}")
async def verify_otp(otp: str, recipient_email: str):
    return await user_service.verify_otp(otp=otp, recipient_email=recipient_email)