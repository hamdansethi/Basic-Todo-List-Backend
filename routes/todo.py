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

router = APIRouter()  # Create a new FastAPI router for todo endpoints

# Create a new todo item for the current logged-in user
@router.post("/", response_model=TodoResponse)
async def create_todo_route(todo: TodoCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Call the controller to create a todo, passing the todo data, username and DB session
    return await create_todo(todo, current_user.username, db)

# Get all todos visible to the current user (all if admin, else user's own todos)
@router.get("/", response_model=List[TodoResponse])
async def get_all_todos_route(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Call the controller to get todos filtered by user role and username
    return await get_all_todos(current_user.username, current_user.role, db)

# Get a specific todo by its ID if the current user is authorized to access it
@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo_route(todo_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Retrieve the todo by ID and check access rights inside controller
    todo = await get_todo_by_id(todo_id, current_user.username, current_user.role, db)
    if not todo:
        # If todo doesn't exist, return HTTP 404 error
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

# Update a specific todo by its ID, only if the user has permission
@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo_route(todo_id: int, todo: TodoUpdate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Call controller to update the todo with new data
    updated_todo = await update_todo(todo_id, todo, current_user.username, current_user.role, db)
    if not updated_todo:
        # If todo not found, return HTTP 404 error
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo

# Delete a todo by ID, only accessible by admin users
@router.delete("/{todo_id}", response_model=dict)
async def delete_todo_route(todo_id: int, current_user: dict = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    # Admin-only: delete the todo from database
    deleted = await delete_todo(todo_id, db)
    if not deleted:
        # If todo not found, return HTTP 404 error
        raise HTTPException(status_code=404, detail="Todo not found")
    # Return success message after deletion
    return {"message": "Todo deleted successfully"}
