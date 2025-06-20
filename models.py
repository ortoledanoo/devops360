from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str
    totp: str = None

class User(BaseModel):
    username: str
    email: EmailStr
    created_at: datetime
    two_fa_enabled: bool = True 