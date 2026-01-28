import os
from typing import Optional, Annotated
from database.core import get_db
from login.models import LoginRequestModel, SignupRequestModel, TokenRefreshRequest
from tables.auth import User
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import logging
from sqlalchemy.orm import Session
from database.core import DbSession
logging.basicConfig(level=logging.INFO)
from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta, timezone
from core.config import config
password_hash = PasswordHash.recommended()

class SignupResponseModel(BaseModel):
    email: str
    is_active: bool
class TokenResponseModel(BaseModel):
    access_token: str
    token_type: str = "bearer"

router = APIRouter(prefix="/login", tags=["Login"])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

def create_access_token(user: User, expires_delta: Optional[int] = None):
    # expires_delta is expected in minutes
    if expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=config.access_token_expire_minutes)
    
    encode = {"user_id": str(user.id), "email": user.email, "exp": int(expire.timestamp()), "type": "access"}
    return jwt.encode(encode, config.secret_key, algorithm=config.jwt_algorithm)

def create_refresh_token(user: User, expires_delta: Optional[int] = None):
    if expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(days=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=config.refresh_token_expire_days)
        
    encode = {"user_id": str(user.id), "email": user.email, "exp": int(expire.timestamp()), "type": "refresh"}
    return jwt.encode(encode, config.secret_key, algorithm=config.jwt_algorithm)

@router.post("/signup", response_model=SignupResponseModel)
async def signup(req: SignupRequestModel,db: DbSession):
    user_model=User(email=req.email,hashed_password=get_password_hash(req.password))
    db.add(user_model)
    db.commit()
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return SignupResponseModel(email=user.email, is_active=user.is_active)


@router.post("/signin")
async def signin(
    db: DbSession,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)




    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "is_active": user.is_active,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=TokenResponseModel)
async def refresh_token(req: TokenRefreshRequest, db: DbSession):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(req.refresh_token, config.secret_key, algorithms=[config.jwt_algorithm])
        user_id: str = payload.get("user_id")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise credentials_exception
            
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
        
    new_access_token = create_access_token(user)
    return {"access_token": new_access_token, "token_type": "bearer"}





