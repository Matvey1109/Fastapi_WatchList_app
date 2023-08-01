from fastapi import FastAPI
from src.tasks.router import router as router_tasks
from src.users.router import router as router_users
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

app = FastAPI(
    title="ToDo_app"
)

app.include_router(router_tasks)
app.include_router(router_users)


@app.get("/")
def get():
    return {"message": "success"}


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
