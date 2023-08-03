from sqlalchemy import Column, Integer, Float, String, ForeignKey, Boolean, DateTime
from src.database import Base
from src.users.models import User
from datetime import datetime


class Movie(Base):
    __tablename__ = "movie"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    year = Column(String)
    your_score = Column(Integer, default=None)
    average_score = Column(Float)
    original_language = Column(String, index=True)
    poster_path = Column(String, index=True)
    watched = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey(User.id))
