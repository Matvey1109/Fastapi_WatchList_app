from pydantic import BaseModel


class AddMovie(BaseModel):
    Title: str
    Year: int
