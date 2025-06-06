from sqlalchemy import Column, Integer, String, DateTime  # SQLAlchemy types for table columns
from database import Base  # Base class for SQLAlchemy models, typically from declarative_base()
from pydantic import BaseModel, ConfigDict  # For request and response validation
from datetime import datetime  # To set timestamp fields

# SQLAlchemy model representing a Todo item in the database
class Todo(Base):
    __tablename__ = "todos"  # This sets the table name in the DB to 'todos'

    id = Column(Integer, primary_key=True, index=True)  # Unique ID for each todo (auto-increment)
    title = Column(String, index=True)  # Title of the todo
    description = Column(String, nullable=True)  # Optional detailed description
    username = Column(String, nullable=False)  # The username who created this todo
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # Timestamp when created
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)  # Timestamp when last updated

# Pydantic model used for creating a new todo (from request body)
class TodoCreate(BaseModel):
    title: str  # Required title field
    description: str | None = None  # Optional description

# Pydantic model used when updating an existing todo
class TodoUpdate(BaseModel):
    title: str | None = None  # Title is optional during update
    description: str | None = None  # Description is optional during update

# Pydantic model used when returning a todo to the client
class TodoResponse(BaseModel):
    id: int  # ID of the todo
    title: str  # Title of the todo
    description: str | None  # Optional description
    username: str  # User who created it
    created_at: datetime  # When it was created
    updated_at: datetime  # When it was last updated

    model_config = ConfigDict(from_attributes=True)  # Allows creating this Pydantic model from ORM objects (like SQLAlchemy rows)
