from sqlalchemy import Column, Integer  # SQLAlchemy column types
from sqlalchemy.types import String  # SQLAlchemy string type
from database import Base  # Base class for SQLAlchemy models
from pydantic import BaseModel, ConfigDict, Field  # For data validation and schema definition

# SQLAlchemy model representing a user in the database
class User(Base):
    __tablename__ = "users"  # Table name in the database will be 'users'

    id = Column(Integer, primary_key=True, index=True)  # Unique ID (auto-incremented)
    username = Column(String, unique=True, index=True, nullable=False)  # Unique username, required
    password = Column(String, nullable=False)  # Password stored in hashed format
    role = Column(String, nullable=False, default="user")  # Role of the user, defaults to "user"

# Pydantic model used when creating a new user (e.g., from request body)
class UserCreate(BaseModel):
    username: str  # Required username
    password: str  # Required password (to be hashed later)
    role: str = Field(default="user", pattern="^(user|admin)$")  # Optional role, must be 'user' or 'admin'

# Pydantic model used when returning user data in API responses (excluding password)
class UserResponse(BaseModel):
    id: int  # User ID
    username: str  # Username
    role: str  # Role (admin or user)

    model_config = ConfigDict(from_attributes=True)  # Allows conversion from SQLAlchemy model to Pydantic model
