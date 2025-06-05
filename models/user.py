from sqlalchemy import Column, Integer
from sqlalchemy.types import String
from database import Base
from pydantic import BaseModel, ConfigDict, Field

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # Hashed password
    role = Column(String, nullable=False, default="user")

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = Field(default="user", pattern="^(user|admin)$")  # Allow user or admin

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True)