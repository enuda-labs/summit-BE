from fastapi import APIRouter, HTTPException
from app.models.auth_models import User, User_Pydantic, UserIn_Pydantic
from typing import List
from app.services import user as user_service

router = APIRouter()

@router.post("/register", response_model=User_Pydantic)
async def register_user(user: UserIn_Pydantic):
    return await user_service.create_user(user=user)

@router.get("/all/users", response_model=List[User_Pydantic])
async def get_all_users():
    return await user_service.get_all_users()

@router.get("/users/{user_id}", response_model=User_Pydantic)
async def read_user(user_id: int):
    return await user_service.get_user(user_id=user_id)

@router.put("/users/{user_id}", response_model=User_Pydantic)
async def update_user_details(user_id: int, user: UserIn_Pydantic):
    return await user_service.update_user(user_id=user_id, user=user)