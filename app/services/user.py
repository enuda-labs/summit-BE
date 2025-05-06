from passlib.context import CryptContext
from fastapi import HTTPException
from app.models.user import User, User_Pydantic
from typing import List
from datetime import datetime
import random
import string
from tortoise.exceptions import IntegrityError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def get_user_by_email(email: str) -> User:
    return await User.get_or_none(email=email)

async def get_user_by_username(username: str) -> User:
    return await User.get_or_none(username=username)

async def create_user(user_data: dict) -> User_Pydantic:
    """Create a new user"""
    try:
        user = await User.create(**user_data)
        return await User_Pydantic.from_tortoise_orm(user)
    except IntegrityError as e:
        if "email" in str(e):
            raise ValueError("Email already exists")
        elif "username" in str(e):
            raise ValueError("Username already exists")
        raise e

async def get_all_users() -> list[User_Pydantic]:
    """Get all users"""
    return await User_Pydantic.from_queryset(User.all())

async def get_user(user_id: int) -> User_Pydantic:
    """Get a user by ID"""
    user = await User.get_or_none(id=user_id)
    if not user:
        raise ValueError("User not found")
    return await User_Pydantic.from_tortoise_orm(user)

async def update_user(user_id: int, user_data: dict) -> User_Pydantic:
    """Update a user"""
    user = await User.get_or_none(id=user_id)
    if not user:
        raise ValueError("User not found")

    # Check for unique constraints
    if "email" in user_data:
        existing_user = await User.get_or_none(email=user_data["email"])
        if existing_user and existing_user.id != user_id:
            raise ValueError("Email already exists")

    if "username" in user_data:
        existing_user = await User.get_or_none(username=user_data["username"])
        if existing_user and existing_user.id != user_id:
            raise ValueError("Username already exists")

    # Update user
    await user.update_from_dict(user_data).save()
    return await User_Pydantic.from_tortoise_orm(user)

async def generate_otp(user_id: int, email: str) -> str:
    """
    Generate a 5-digit alphanumeric OTP.
    
    Args:
        user_id: ID of the user
        email: Email address of the user
        
    Returns:
        str: The generated OTP
    """
    # Generate a 5-digit alphanumeric OTP
    characters = string.ascii_letters + string.digits
    otp = ''.join(random.choices(characters, k=5))
    
    # TODO: Implement OTP storage with Tortoise ORM
    # This will need a new OTP model using Tortoise ORM
    
    return otp