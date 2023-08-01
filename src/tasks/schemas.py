from pydantic import BaseModel


class CreateTask(BaseModel):
    title: str
    description: str
