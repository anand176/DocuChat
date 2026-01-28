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
from pwdlib import PasswordHash
password_hash = PasswordHash.recommended()

class LoginResponseModel(BaseModel):
    email: str
    is_active: bool

router = APIRouter(prefix="/login", tags=["Login"])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

@router.post("/signup", response_model=LoginResponseModel)
async def signup(req: LoginRequestModel,db: DbSession):
    user_model=User(email=req.email,hashed_password=get_password_hash(req.password))
    db.add(user_model)
    db.commit()
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return LoginResponseModel(email=user.email, is_active=user.is_active)





