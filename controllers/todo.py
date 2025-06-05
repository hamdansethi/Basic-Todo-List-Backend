# controllers/todo.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.todo import Todo, TodoCreate, TodoUpdate, TodoResponse

async def create_todo(todo: TodoCreate, username: str, db: Session):
    db_todo = Todo(**todo.dict(), username=username)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return TodoResponse.from_orm(db_todo)

async def get_all_todos(username: str, role: str, db: Session):
    if role == "admin":
        return [TodoResponse.from_orm(todo) for todo in db.query(Todo).all()]
    return [TodoResponse.from_orm(todo) for todo in db.query(Todo).filter(Todo.username == username).all()]

async def get_todo_by_id(todo_id: int, username: str, role: str, db: Session):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        return None
    if role != "admin" and todo.username != username:
        raise HTTPException(status_code=403, detail="Not authorized to access this todo")
    return TodoResponse.from_orm(todo)

async def update_todo(todo_id: int, todo: TodoUpdate, username: str, role: str, db: Session):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        return None
    if role != "admin" and db_todo.username != username:
        raise HTTPException(status_code=403, detail="Not authorized to update this todo")
    for key, value in todo.dict(exclude_unset=True).items():
        setattr(db_todo, key, value)
    db.commit()
    db.refresh(db_todo)
    return TodoResponse.from_orm(db_todo)

async def delete_todo(todo_id: int, db: Session):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        return False
    db.delete(db_todo)
    db.commit()
    return True