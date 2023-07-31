from pydantic import BaseModel
from datetime import datetime


class CreateTask(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime
