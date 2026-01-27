from pydantic import BaseModel, EmailStr

class LoginRequestModel(BaseModel):
    email: EmailStr
    password: str