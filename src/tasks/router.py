from fastapi import APIRouter, Depends, HTTPException, status
from src.tasks.models import Task
from src.tasks.schemas import CreateTask
from src.database import AsyncSession, get_async_session
from sqlalchemy import select, insert
from datetime import datetime

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
async def add_task(new_task: CreateTask, session: AsyncSession = Depends(get_async_session)):
    try:
        query = insert(Task).values(**new_task.model_dump())
        query_all_tasks = select(Task).where(Task.id == new_task.id)
        all_tasks = await session.execute(query_all_tasks)
        if len(all_tasks.fetchall()) > 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await session.execute(query)
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
            "details": "There is already task with this id"
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@router.delete("")
async def delete_task_by_id(task_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(Task).where(Task.id == task_id)
        task = await session.execute(query)
        if not task.scalar():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await session.delete(task.scalar_one())
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
            "details": "Task is not found"
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@router.put("")
async def update_task_by_id(task_id: int, title: str = None, description: str = None, completed: bool = None,
                      session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(Task).where(Task.id == task_id)
        task = await session.execute(query)
        if not task.scalar():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        task = task.scalar_one()
        if title:
            task.title = title
        if description:
            task.description = description
        if completed is not None:
            task.completed = completed
        task.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(task)
        return {
            "status": "success",
            "data": None,
            "details": None
        }
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "status": "error404",
            "data": None,
            "details": "Task is not found"
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "status": "error",
            "data": None,
            "details": None
        })
