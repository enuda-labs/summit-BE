from passlib.context import CryptContext
from fastapi import HTTPException
from app.models.user import User, User_Pydantic, OTPSystem, OTP_Pydantic, UserRegister, OTPVerify
from typing import List
from datetime import datetime, timedelta, timezone
import random
import string
from tortoise.exceptions import IntegrityError
from app.services.smtp import send_email
from tortoise.signals import post_save
import logging
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def get_user_by_email(email: str) -> User:
    return await User.get_or_none(email=email)

async def get_user_by_username(username: str) -> User:
    return await User.get_or_none(username=username)

async def create_user(user_data: UserRegister) -> User_Pydantic:
    """Create a new user"""
    try:
        # Hash the password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user with hashed password
        user = await User.create(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name
        )
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


@post_save(User)
async def generate_otp(sender, instance, created, using_db=None, update_fields=None):
    """Generate a 6-digit OTP and send it to the user's email"""
    if created:
        try:
            # Check if user exists
            user = await User.get_or_none(id=instance.id)
            if not user:
                raise ValueError("User not found")
            
            # Generate OTP
            otp = await OTPSystem.create(user=user)
            await otp.save()

            # Ensure OTP is a string
            otp_str = str(otp.otp)
            logger.info(f"Generated OTP for user {user.email}: {otp_str}")

            # Send email with OTP
            try:
                await send_email(otp_str, user.username, user.email)
                logger.info(f"OTP sent to {user.email}")
            except HTTPException as e:
                logger.error(f"Error sending OTP to {user.email}: {e.detail}")
                # Don't raise the exception, just log it
                # This way the user registration still succeeds even if email fails
                
        except Exception as e:
            logger.error(f"Error in generate_otp: {str(e)}")
            # Don't raise the exception, just log it
            # This way the user registration still succeeds even if OTP generation fails


async def verify_otp(otp: str, recipient_email: str) -> dict:
    """Verify OTP for a user"""
    try:
        # Get user by email
        user = await User.get_or_none(email=recipient_email)
        if not user:
            raise ValueError("User not found")

        # Get the most recent OTP for the user
        otp_record = await OTPSystem.filter(user=user).order_by('-created_at').first()
        if not otp_record:
            raise ValueError("No OTP found for this user")

        # Check if OTP is expired (20 minutes)
        current_time = datetime.now(timezone.utc)
        if current_time - otp_record.created_at > timedelta(minutes=20):
            raise ValueError("OTP has expired")

        # Verify OTP
        if str(otp_record.otp) != str(otp):
            raise ValueError("Invalid OTP")

        # Activate user
        user.is_active = True
        await user.save()

        # Delete used OTP
        await otp_record.delete()

        return {
            "status": "success",
            "message": "OTP verified successfully",
            "user": await User_Pydantic.from_tortoise_orm(user)
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error verifying OTP: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while verifying OTP"
        )


async def delete_user(user_email: str) -> User_Pydantic:
    """Delete a user by email"""
    user = await User.get_or_none(email=user_email)
    if not user:
        raise ValueError("User not found")
    await user.delete()
    return JSONResponse(content={"message": "User deleted successfully"})
    