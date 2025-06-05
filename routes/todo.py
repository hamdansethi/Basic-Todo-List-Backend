# routes/todo.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from controllers.todo import (
    create_todo,
    get_all_todos,
    get_todo_by_id,
    update_todo,
    delete_todo,
)
from models.todo import TodoCreate, TodoUpdate, TodoResponse
from typing import List
from middleware.auth import get_current_user, get_current_admin_user
from database import get_db

router = APIRouter()

@router.post("/", response_model=TodoResponse)
async def create_todo_route(todo: TodoCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return await create_todo(todo, current_user.username, db)

@router.get("/", response_model=List[TodoResponse])
async def get_all_todos_route(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return await get_all_todos(current_user.username , current_user.role, db)

@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo_route(todo_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    todo = await get_todo_by_id(todo_id, current_user.username, current_user.role, db)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo_route(todo_id: int, todo: TodoUpdate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    updated_todo = await update_todo(todo_id, todo, current_user.username, current_user.role, db)
    if not updated_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo

@router.delete("/{todo_id}", response_model=dict)
async def delete_todo_route(todo_id: int, current_user: dict = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    deleted = await delete_todo(todo_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}