from typing import Optional
from database.core import get_db
from login.models import LoginRequestModel
from tables.auth import User
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import logging
from sqlalchemy.orm import Session
from database.core import DbSession
logging.basicConfig(level=logging.INFO)

class LoginResponseModel(BaseModel):
    email: str
    is_active: bool

router = APIRouter(prefix="/login", tags=["Login"])



@router.post("/signup", response_model=LoginResponseModel)
async def signup(req: LoginRequestModel,db: DbSession):
    # Implement signup logic here
    user_model=User(email=req.email,hashed_password=req.password)
    db.add(user_model)
    db.commit()
    user = db.query(User).filter(User.email == req.email).first()
    if not user or user.hashed_password != req.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return LoginResponseModel(email=user.email, is_active=user.is_active)


