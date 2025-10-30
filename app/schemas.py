from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class DocumentCreate(BaseModel):
    title: str
    content: str


class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentSearchRequest(BaseModel):
    query: str


class DocumentSearchResult(BaseModel):
    id: int
    title: str
    content: str
    similarity: float
    created_at: datetime

    class Config:
        from_attributes = True
