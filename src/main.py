from fastapi import FastAPI
from src.tasks.router import router as router_tasks

app = FastAPI(
    title="ToDo_app"
)

app.include_router(router_tasks)


@app.get("/")
def get():
    return {"message": "success"}
