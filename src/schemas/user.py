from pydantic import BaseModel, EmailStr

from src.models.user import Role


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: Role

    class Config:
        from_attributes = True
