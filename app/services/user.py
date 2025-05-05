from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from fastapi import HTTPException
from typing import Dict, Any, List
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def _user_to_dict(user: User) -> Dict[str, Any]:
    """Convert SQLAlchemy User model to dictionary"""
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }

def get_all_users(db: Session) -> Dict[str, Any]:
    """Get all users from the database"""
    users = db.query(User).all()
    return {
        "status": "success",
        "message": "Users retrieved successfully",
        "data": [_user_to_dict(user) for user in users]
    }

def create_user(db: Session, user: UserCreate) -> Dict[str, Any]:
    # Check if user with email exists
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if user with username exists
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "status": "success",
        "message": "User registered successfully",
        "data": _user_to_dict(db_user)
    }

def get_user(db: Session, user_id: int) -> Dict[str, Any]:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "status": "success",
        "message": "User retrieved successfully",
        "data": _user_to_dict(db_user)
    }

def update_user(db: Session, user_id: int, user: UserUpdate) -> Dict[str, Any]:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return {
        "status": "success",
        "message": "User updated successfully",
        "data": _user_to_dict(db_user)
    }