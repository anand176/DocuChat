from pydantic import BaseModel, EmailStr

class SignupRequestModel(BaseModel):
    email: EmailStr
    password: str

class LoginRequestModel(BaseModel):
    email: EmailStr
    password: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str