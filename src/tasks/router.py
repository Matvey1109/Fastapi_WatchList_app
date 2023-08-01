import time
from fastapi import APIRouter, Depends, HTTPException, status
from src.tasks.models import Task
from src.tasks.schemas import CreateTask
from src.users.router import get_current_user
from src.users.models import User
from src.database import AsyncSession, get_async_session
from sqlalchemy import select, insert, and_
from datetime import datetime
from fastapi_cache.decorator import cache

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.get("")
@cache(expire=30)
async def get_tasks(session: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)):
    try:
        time.sleep(0.3)
        query = select(Task).where(Task.user_id == user.id).order_by(Task.id.desc())
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
async def add_task(new_task: CreateTask, session: AsyncSession = Depends(get_async_session),
                   user: User = Depends(get_current_user)):
    try:
        query_all_tasks = select(Task).where(and_(Task.title == new_task.title, Task.user_id == user.id))
        all_tasks = await session.execute(query_all_tasks)
        if len(all_tasks.fetchall()) > 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        task_values = new_task.model_dump()
        task_values["user_id"] = user.id
        query = insert(Task).values(**task_values)
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
            "details": "There is already task with this title"
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@router.delete("")
async def delete_task_by_title(task_title: str, session: AsyncSession = Depends(get_async_session),
                               user: User = Depends(get_current_user)):
    try:
        query = select(Task).where(and_(Task.user_id == user.id, Task.title == task_title))
        task = await session.execute(query)
        task = task.scalar_one_or_none()
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await session.delete(task)
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
async def update_task_by_title(task_title: str, title: str = None, description: str = None, completed: bool = None,
                               session: AsyncSession = Depends(get_async_session),
                               user: User = Depends(get_current_user)):
    try:
        query = select(Task).where(and_(Task.user_id == user.id, Task.title == task_title))
        task = await session.execute(query)
        task = task.scalar_one_or_none()
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
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
