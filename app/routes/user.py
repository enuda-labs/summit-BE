from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate
from app.services import user as user_service
from typing import Dict, Any

router = APIRouter()

@router.post("/register", response_model=Dict[str, Any])
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db=db, user=user)

@router.get("/all/users", response_model=Dict[str, Any])
def get_all_users(db: Session = Depends(get_db)):
    return user_service.get_all_users(db=db)

@router.get("/users/{user_id}", response_model=Dict[str, Any])
def read_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.get_user(db=db, user_id=user_id)

@router.put("/users/{user_id}", response_model=Dict[str, Any])
def update_user_details(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    return user_service.update_user(db=db, user_id=user_id, user=user)