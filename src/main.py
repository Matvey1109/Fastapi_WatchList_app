from fastapi import FastAPI
from src.tasks.router import router as router_tasks
from src.users.router import router as router_users

app = FastAPI(
    title="ToDo_app"
)

app.include_router(router_tasks)
app.include_router(router_users)


@app.get("/")
def get():
    return {"message": "success"}
