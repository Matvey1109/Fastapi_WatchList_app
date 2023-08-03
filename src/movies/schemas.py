from pydantic import BaseModel


class AddMovie(BaseModel):
    title: str
    year: str
