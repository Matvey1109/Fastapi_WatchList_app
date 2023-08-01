from fastapi import APIRouter, Depends
from src.users.base_config import auth_backend
from src.users.utils import get_user_db
from src.users.models import User
from src.users.schemas import UserRead, UserCreate
from src.users.base_config import fastapi_users

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

router.include_router(fastapi_users.get_auth_router(auth_backend))
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))


@router.get("/users/me", response_model=UserRead)
async def read_user_me(current_user: User = Depends(fastapi_users.current_user(active=True)),
                       user_db=Depends(get_user_db)):
    user = await user_db.get(current_user.id)
    return user
