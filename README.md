# FastAPI Todo App

This is a full-featured Todo application built with FastAPI, a modern Python web framework. It allows users to manage tasks with authentication and role-based access control. Users can register, log in, log out, and perform CRUD (Create, Read, Update, Delete) operations on their todos. Admins can view and delete any todo, while regular users can only manage their own.

The app uses SQLite for persistence, SQLAlchemy for ORM, JWT for authentication, and bcrypt for password hashing, making it secure and scalable. This README provides a detailed guide to the project’s setup, features, code structure, with detailed explanations for each component.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [API Endpoints](#api-endpoints)
- [Code Explanation](#code-explanation)
  - [Main Application (`main.py`)](#main-application-mainpy)
  - [Database Configuration (`database.py`)](#database-configuration-databasepy)
  - [User Model (`models/user.py`)](#user-model-modelsuser.py)
  - [Todo Model (`models/todo.py`)](#todo-model-modelstodo.py)
  - [Authentication Controller (`controllers/auth.py`)](#authentication-controller-controllersauth.py)
  - [Todo Controller (`controllers/todo.py`)](#todo-controller-controllerstodo.py)
  - [Authentication Middleware (`middleware/auth.py`)](#authentication-middleware-middlewareauth.py)
  - [Authentication Routes (`routes/auth.py`)](#authentication-routes-routesauth.py)
  - [Todo Routes (`routes/todo.py`)](#todo-routes-routestodo.py)
  - [Dependencies (`requirements.txt`)](#dependencies-requirementstxt)
- [Usage](#usage)
- [Testing](#testing)
- [Notes for Production](#notes-for-production)
- [Contributing](#contributing)
- [License](#license)

## Features
- **User Management**:
  - Register new users with a username, password, and role (user or admin).
  - Log in to receive a JWT token.
  - Log out by blacklisting the JWT token.
- **Todo Management**:
  - Create, read, update, and delete todos.
  - Users can only manage their own todos.
  - Admins can view and delete any todo.
- **Security**:
  - Passwords are hashed using bcrypt.
  - JWT-based authentication with token expiration.
  - Token blacklisting for logout.
- **Persistence**:
  - SQLite database with SQLAlchemy ORM.
  - Stores users and todos in `todos.db`.
- **Role-Based Access Control**:
  - Admins have elevated privileges.
  - Regular users are restricted to their own data.

## Technologies Used
- **FastAPI**: Web framework for building APIs.
- **SQLAlchemy**: ORM for database interactions.
- **SQLite**: Lightweight database.
- **PyJWT**: JWT token generation and validation.
- **passlib[bcrypt]**: Password hashing.
- **python-multipart**: Form data parsing for login.
- **Uvicorn**: ASGI server for running the app.
- **Python 3.11+**: Programming language.

## Project Structure

Basic-Todo-Backend-Using-FastAPI/├── controllers/│   ├── auth.py        # Authentication logic (register, login, logout)│   └── todo.py        # Todo CRUD logic├── middleware/│   └── auth.py        # JWT authentication middleware├── models/│   ├── todo.py        # Todo model (SQLAlchemy and Pydantic)│   └── user.py        # User model (SQLAlchemy and Pydantic)├── routes/│   ├── auth.py        # Authentication API routes│   └── todo.py        # Todo API routes├── database.py        # Database configuration and session management├── main.py            # FastAPI app initialization├── requirements.txt   # Project dependencies└── todos.db           # SQLite database (generated)

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd Basic-Todo-Backend-Using-FastAPI


Create a Virtual Environment:
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac


Install Dependencies:
pip install -r requirements.txt


Run the Application:
uvicorn main:app --reload


The app runs at http://localhost:8000.
The --reload flag enables auto-reload for development.


Access the API:

Open http://localhost:8000/docs for the Swagger UI.
Use the API endpoints to register, log in, and manage todos.


Verify Database:
sqlite3 todos.db
.tables

Should list todos and users.


API Endpoints
All endpoints are documented in the Swagger UI (/docs). Below is a summary:
Authentication (/auth)

POST /auth/register: Create a new user.
Body: { "username": "string", "password": "string", "role": "user|admin" }
Response: { "id": int, "username": "string", "role": "string" }


POST /auth/token: Log in to get a JWT token.
Body: form-data with username and password.
Response: { "access_token": "string", "token_type": "bearer" }


POST /auth/logout: Log out by blacklisting the token.
Headers: Authorization: Bearer <token>
Response: { "message": "Logged out successfully" }



Todos (/api)

POST /api/: Create a todo.
Headers: Authorization: Bearer <token>
Body: { "title": "string", "description": "string|null" }
Response: Todo object


GET /api/: Get all todos (admin: all; user: own).
Headers: Authorization: Bearer <token>
Response: List of Todo objects


GET /api/{todo_id}: Get a specific todo.
Headers: Authorization: Bearer <token>
Response: Todo object


PUT /api/{todo_id}: Update a todo.
Headers: Authorization: Bearer <token>
Body: { "title": "string|null", "description": "string|null" }
Response: Updated Todo object


DELETE /api/{todo_id}: Delete a todo (admin only).
Headers: Authorization: Bearer <token>
Response: { "message": "Todo deleted successfully" }



Code Explanation
Main Application (main.py)

Purpose: Initializes the FastAPI app, creates database tables, and mounts API routes.
Key Components:
Imports Todo and User models to register them with SQLAlchemy’s Base.
Uses Base.metadata.create_all(bind=engine) to create todos and users tables in todos.db.
Mounts auth and todo routers with prefixes /auth and /api.
Defines a root endpoint (GET /) returning a welcome message.


Example:from fastapi import FastAPI
from routes import auth, todo
from database import engine, Base
from models.todo import Todo
from models.user import User

app = FastAPI()

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created.")

app.include_router(auth.router, prefix="/auth")
app.include_router(todo.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the Todo app!"}



Database Configuration (database.py)

Purpose: Sets up the SQLite database connection and SQLAlchemy session management.
Key Components:
Defines SQLALCHEMY_DATABASE_URL as sqlite:///./todos.db.
Creates a SQLAlchemy engine with check_same_thread=False for SQLite thread safety.
Sets up SessionLocal for database sessions.
Defines Base for SQLAlchemy models.
Provides get_db dependency to manage database sessions.


Example:from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



User Model (models/user.py)

Purpose: Defines the users table and Pydantic models for user-related API operations.
Key Components:
SQLAlchemy Model (User):
Table: users
Columns: id (primary key), username (unique), password (hashed), role (default: "user")


Pydantic Models:
UserCreate: Input for registration (username, password, role).
UserResponse: Output for API responses (id, username, role).
Uses Field with regex ^(user|admin)$ to restrict role.




Example:from sqlalchemy import Column, Integer
from sqlalchemy.types import String
from database import Base
from pydantic import BaseModel, ConfigDict, Field

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = Field(default="user", pattern="^(user|admin)$")

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    model_config = ConfigDict(from_attributes=True)



Todo Model (models/todo.py)

Purpose: Defines the todos table and Pydantic models for todo-related API operations.
Key Components:
SQLAlchemy Model (Todo):
Table: todos
Columns: id (primary key), title, description (nullable), username, created_at, updated_at


Pydantic Models:
TodoCreate: Input for creating todos (title, description).
TodoUpdate: Input for updating todos (optional fields).
TodoResponse: Output for API responses (all fields).




Example:from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    username = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class TodoCreate(BaseModel):
    title: str
    description: str | None = None

class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    username: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)



Authentication Controller (controllers/auth.py)

Purpose: Handles user authentication logic (register, login, logout).
Key Components:
Password Hashing: Uses passlib with bcrypt to hash and verify passwords.
User Management: Functions to create and retrieve users from the users table.
JWT Tokens: Generates tokens with PyJWT, including sub (username) and role.
Token Blacklist: Maintains an in-memory set of blacklisted tokens for logout.
Functions:
hash_password, verify_password: Password management.
get_user, create_user: User database operations.
authenticate_user: Validates credentials.
create_access_token: Generates JWT.
blacklist_token, is_token_blacklisted: Manages logout.




Example:from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta
from models.user import User, UserCreate
from database import get_db
from typing import Set

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
blacklisted_tokens: Set[str] = set()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def get_user(username: str, db: Session):
    return db.query(User).filter(User.username == username).first()

def create_user(user: UserCreate, db: Session):
    if get_user(user.username, db):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(username: str, password: str, db: Session):
    user = get_user(username, db)
    if not user or not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def blacklist_token(token: str):
    blacklisted_tokens.add(token)

def is_token_blacklisted(token: str) -> bool:
    return token in blacklisted_tokens



Todo Controller (controllers/todo.py)

Purpose: Implements Todo CRUD logic.
Key Components:
Functions for creating, reading, updating, and deleting todos.
Enforces role-based access: admins can view all todos; users see only their own.
Uses SQLAlchemy for database operations and Pydantic for response formatting.
Functions:
create_todo: Creates a new todo.
get_all_todos: Retrieves todos based on role.
get_todo_by_id: Fetches a specific todo with authorization.
update_todo: Updates a todo with authorization.
delete_todo: Deletes a todo (admin only).




Example:from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.todo import Todo, TodoCreate, TodoUpdate, TodoResponse
from models.user import User

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



Authentication Middleware (middleware/auth.py)

Purpose: Validates JWT tokens and enforces authentication.
Key Components:
Defines oauth2_scheme using OAuth2PasswordBearer for token extraction.
get_current_user: Validates tokens, checks blacklist, and retrieves the user.
get_current_admin_user: Ensures the user is an admin.
Handles token decoding, expiration, and blacklisting.


Example:from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from controllers.auth import SECRET_KEY, ALGORITHM, get_user, is_token_blacklisted
from sqlalchemy.orm import Session
from database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token is invalid (logged out)")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(username, db)
    if user is None:
        raise credentials_exception
    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user



Authentication Routes (routes/auth.py)

Purpose: Defines API endpoints for authentication.
Key Components:
/register: Creates a new user.
/token: Authenticates and returns a JWT token.
/logout: Blacklists the token.
Uses OAuth2PasswordRequestForm for login form data.


Example:from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from controllers.auth import authenticate_user, create_access_token, create_user, blacklist_token
from models.user import UserCreate, UserResponse
from database import get_db
from pydantic import BaseModel
from middleware.auth import oauth2_scheme

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(user, db)
    return db_user

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    blacklist_token(token)
    return {"message": "Logged out successfully"}



Todo Routes (routes/todo.py)

Purpose: Defines API endpoints for Todo operations.
Key Components:
Endpoints for creating, reading, updating, and deleting todos.
Uses get_current_user for authentication and get_current_admin_user for admin-only actions.
Integrates with controllers.todo for business logic.


Example:from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from controllers.todo import (
    create_todo,
    get_all_todos,
    get_todo_by_id,
    update_todo,
    delete_todo,
)
from models.todo import TodoCreate, TodoUpdate, TodoResponse
from models.user import User
from typing import List
from middleware.auth import get_current_user, get_current_admin_user
from database import get_db

router = APIRouter()

@router.post("/", response_model=TodoResponse)
async def create_todo_route(todo: TodoCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await create_todo(todo, current_user.username, db)

@router.get("/", response_model=List[TodoResponse])
async def get_all_todos_route(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await get_all_todos(current_user.username, current_user.role, db)

@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo_route(todo_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    todo = await get_todo_by_id(todo_id, current_user.username, current_user.role, db)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo_route(todo_id: int, todo: TodoUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    updated_todo = await update_todo(todo_id, todo, current_user.username, current_user.role, db)
    if not updated_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo

@router.delete("/{todo_id}", response_model=dict)
async def delete_todo_route(todo_id: int, current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    deleted = await delete_todo(todo_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}



Dependencies (requirements.txt)

Purpose: Lists all Python packages required to run the app.
Content:fastapi
uvicorn
PyJWT
passlib[bcrypt]
python-multipart
sqlalchemy


Installation:pip install -r requirements.txt



Usage

Start the Server:
uvicorn main:app --reload


Register Users:

Use POST /auth/register to create users, e.g.:{
  "username": "alice",
  "password": "secret",
  "role": "admin"
},
{
  "username": "bob",
  "password": "password123",
  "role": "user"
}




Log In:

Use POST /auth/token with form-data:
username: : alice
password: : secret


Copy the access_token.


Authorize:

In Swagger UI, click “Authorize” and enter Bearer <token>.


Manage Todos:

Create: POST /api/ with { "title": "Pray", "description": "Fajar" }`
Get: GET /api/ (alice sees all todos; Bob sees only his)
Update: PUT /api/{id}
Delete: DELETE /api/{id} (admin only)


Log Out:

Use POST /auth/logout: with the token to invalidate it.



Testing

Test with Swagger UI (http://localhost:8000/docs`):

Test all endpoints interactively.


Manual Testing (e.g., with curl or Postman):

Register:curl -X POST "http://localhost:8000/auth/register" -H "Content-Type: application/json" -d '{"username":"alice","password":"secret","role":"admin"}'


Login:curl -X POST "http://localhost:8000/auth/token" -F "username=alice" -F "password=secret"


Create Todo:curl -X POST "http://localhost:8000/api/" -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"title":"Pray","description":"Fajar"}'




Database Verification:
  -sqlite3
 todos.db
.tables
sqlite3 todos.db
SELECT * FROM users;
SELECT * FROM todos



Notes for Production

Secure Secret Key**:-Generate a secure SECRET_KEY:import secrets
print(secrets.token_hex(32))

  Store in a .env file using python-dotenv.
Token Blacklist: The in-memory blacklisted_tokens set is not persistent. Use Redis or a database table for production.
Database: Replace SQLite with SQLite PostgreSQL or MySQL for scalability.
Alembic: Add Alembic migrations for database migrations to handle schema changes.
HTTPS: Deploy with a production server (e.g., gunicorn) and enable HTTPS.
Logging: Add logging for monitoring and debugging.
Contributing:Contributions welcome! To contribute:


Fork the repository,.
Create a branch (git checkout -b feature/your-feature).
Commit changes (git commit -m "Add feature").
Push to your fork (git push origin feature/your-feature).
Open a pull request.

License
MIT License

Built with ❤️ using FastAPI```
