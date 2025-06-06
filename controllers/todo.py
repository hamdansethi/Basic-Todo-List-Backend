from fastapi import HTTPException  # For throwing errors like "Not allowed!"
from sqlalchemy.orm import Session  # Helps us talk to the database
from models.todo import Todo, TodoCreate, TodoUpdate, TodoResponse  # Data models for creating, updating, and showing todos

# Create a new todo item
async def create_todo(todo: TodoCreate, username: str, db: Session):
    # Make a Todo object from the input data and add the username
    db_todo = Todo(**todo.dict(), username=username)
    db.add(db_todo)            # Add to database session
    db.commit()                # Save changes to database
    db.refresh(db_todo)        # Get the latest info from database
    return TodoResponse.from_orm(db_todo)  # Return a clean version of the todo

# Get all todos for a user or all users if the user is an admin
async def get_all_todos(username: str, role: str, db: Session):
    if role == "admin":  # Admin can see everything
        return [TodoResponse.from_orm(todo) for todo in db.query(Todo).all()]
    # Regular users only see their own todos
    return [TodoResponse.from_orm(todo) for todo in db.query(Todo).filter(Todo.username == username).all()]

# Get one todo by its ID
async def get_todo_by_id(todo_id: int, username: str, role: str, db: Session):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()  # Find the todo
    if not todo:
        return None  # If it doesn't exist, return nothing
    if role != "admin" and todo.username != username:
        # If not admin and not the owner of the todo, don't allow access
        raise HTTPException(status_code=403, detail="Not authorized to access this todo")
    return TodoResponse.from_orm(todo)  # Return the todo in a clean format

# Update a todo by ID
async def update_todo(todo_id: int, todo: TodoUpdate, username: str, role: str, db: Session):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()  # Get the todo
    if not db_todo:
        return None  # If not found, return nothing
    if role != "admin" and db_todo.username != username:
        # If not admin and not the owner, throw error
        raise HTTPException(status_code=403, detail="Not authorized to update this todo")
    # Go through each value sent and update the todo
    for key, value in todo.dict(exclude_unset=True).items():
        setattr(db_todo, key, value)
    db.commit()         # Save changes
    db.refresh(db_todo) # Get updated data
    return TodoResponse.from_orm(db_todo)  # Return updated todo

# Delete a todo by ID
async def delete_todo(todo_id: int, db: Session):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()  # Find the todo
    if not db_todo:
        return False  # If it doesn't exist, return False
    db.delete(db_todo)  # Delete the todo
    db.commit()         # Save changes
    return True         # Return True to show it was deleted
