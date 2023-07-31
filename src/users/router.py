from fastapi import APIRouter, Depends, HTTPException, status
from src.users.models import User
from src.users.schemas import CreateUser, LoginUser, UserOut
from src.database import AsyncSession, get_async_session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


def hash_password(password: str):
    return "hash" + password


def verify_password(plain_password: str, hashed_password):
    return hashed_password == "hash" + plain_password


@router.post("/register", response_model=UserOut)
async def register_user(user: CreateUser, session: AsyncSession = Depends(get_async_session)):
    try:
        new_user = User(
            username=user.username,
            email=user.email,
            password_hash=hash_password(user.password),
            created_at=datetime.utcnow()
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={
            "status": "error",
            "data": None,
            "details": "User already exists"
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@router.post("/login", response_model=UserOut)
async def login_user(user: LoginUser, session: AsyncSession = Depends(get_async_session)):
    query = select(User).where(User.email == user.email)
    existing_user = await session.execute(query)
    existing_user = existing_user.scalar_one()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "status": "error",
            "data": None,
            "details": "User not found"
        })
    if not verify_password(user.password, existing_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={
            "status": "error",
            "data": None,
            "details": "Incorrect password"
        })
    await session.commit()
    return existing_user
