from pydantic import BaseModel
from datetime import datetime


class CreateUser(BaseModel):
    username: str
    email: str
    password: str


class LoginUser(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        orm_mode = True
