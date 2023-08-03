import time
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from src.movies.models import Movie
from src.movies.schemas import AddMovie
from src.movies.tmdb_api import get_movie_from_api
from src.users.router import get_current_user
from src.users.models import User
from src.database import AsyncSession, get_async_session
from sqlalchemy import select, insert, and_, func
from datetime import datetime
from fastapi_cache.decorator import cache

router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)


@router.get("/get_my_movies")
@cache(expire=30)
async def get_my_movies(session: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)):
    try:
        time.sleep(0.3)
        query = select(Movie).where(Movie.user_id == user.id).order_by(Movie.id.desc())
        result = await session.execute(query)
        data = [{f"Movie, ID#{row[0].id}": row[0]} for row in result]
        return {
            "status": "success",
            "data": data,
            "details": None
        }
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@router.post("/add_movie")
async def add_movie(new_movie: AddMovie, session: AsyncSession = Depends(get_async_session),
                    user: User = Depends(get_current_user)):
    try:
        query_all_movies = select(Movie).where(
            and_(func.upper(Movie.title) == func.upper(new_movie.title), Movie.user_id == user.id))
        all_movies = await session.execute(query_all_movies)
        if len(all_movies.fetchall()) > 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)

        movie_info = get_movie_from_api(new_movie.title, new_movie.year)
        movie_values = dict()
        movie_values["title"] = movie_info["title"]
        movie_values["description"] = movie_info["overview"]
        movie_values["year"] = new_movie.year
        movie_values["average_score"] = movie_info["vote_average"]
        movie_values["original_language"] = movie_info["original_language"]
        movie_values["poster_path"] = "https://image.tmdb.org/t/p/original" + movie_info["poster_path"]
        movie_values["user_id"] = user.id
        query = insert(Movie).values(**movie_values)
        await session.execute(query)
        await session.commit()
        return {
            "status": "success",
            "data": movie_values,
            "details": None
        }
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={
            "status": "error404",
            "data": None,
            "details": "There is already movie in your list"
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@router.delete("/delete_movie_by_title")
async def delete_movie_by_title(movie_title: str, year: str, session: AsyncSession = Depends(get_async_session),
                                user: User = Depends(get_current_user)):
    try:
        query = select(Movie).where(
            and_(and_(func.upper(Movie.title) == func.upper(movie_title), Movie.year == year),
                 Movie.user_id == user.id))
        movie = await session.execute(query)
        movie = movie.scalar_one_or_none()
        if movie is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await session.delete(movie)
        await session.commit()
        return {
            "status": "success",
            "data": None,
            "details": None
        }
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "status": "error404",
            "data": None,
            "details": "Movie is not found"
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@router.put("/update_movie_by_title")
async def update_movie_by_title(movie_title: str, year: str, watched: bool = None, your_score: int = None,
                                session: AsyncSession = Depends(get_async_session),
                                user: User = Depends(get_current_user)):
    try:
        query = select(Movie).where(
            and_(and_(func.upper(Movie.title) == func.upper(movie_title), Movie.year == year),
                 Movie.user_id == user.id))
        movie = await session.execute(query)
        movie = movie.scalar_one_or_none()
        if movie is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if watched is not None:
            movie.watched = watched
        if your_score is not None:
            movie.your_score = your_score
        movie.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(movie)
        return {
            "status": "success",
            "data": None,
            "details": None
        }
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "status": "error404",
            "data": None,
            "details": "Movie is not found"
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@router.get("/get_poster")
def get_poster(title: str, year: str):
    movie_info = get_movie_from_api(title, year)
    result = "https://image.tmdb.org/t/p/original" + movie_info["poster_path"]
    return RedirectResponse(result)
