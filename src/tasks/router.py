from fastapi import APIRouter, Depends, HTTPException, status
from src.tasks.models import Task
from src.tasks.schemas import CreatedTask
from src.database import AsyncSession, get_async_session
from sqlalchemy import select, insert

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.get("")
async def get_tasks(session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(Task).order_by(Task.id.desc()).limit(5)
        result = await session.execute(query)
        data = [{f"Task №{row[0].id}": row[0]} for row in result]
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


@router.post("")
async def add_task(new_task: CreatedTask, session: AsyncSession = Depends(get_async_session)):
    try:
        query = insert(Task).values(**new_task.model_dump())
        await session.execute(query)
        await session.commit()
        return {
            "status": "success",
            "data": None,
            "details": None
        }
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "status": "error",
            "data": None,
            "details": None
        })
