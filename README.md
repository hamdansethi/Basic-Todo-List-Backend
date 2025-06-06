# FastAPI Todo App

A full-featured Todo application built with **FastAPI**, allowing user management with authentication and role-based access control. Users can register, log in, log out, and manage their todos, while admins have elevated privileges.

---

## Table of Contents

* [Features](#features)
* [Technologies Used](#technologies-used)
* [Project Structure](#project-structure)
* [Setup Instructions](#setup-instructions)
* [API Endpoints](#api-endpoints)
* [Code Explanation](#code-explanation)
* [Usage](#usage)
* [Testing](#testing)
* [Notes for Production](#notes-for-production)
* [Contributing](#contributing)
* [License](#license)

---

## Features

* **User Management**

  * Register with username, password, and role (`user` or `admin`).
  * Login to receive JWT access tokens.
  * Logout by blacklisting tokens.
* **Todo Management**

  * Create, read, update, and delete todos.
  * Users manage their own todos.
  * Admins can view and delete any todo.
* **Security**

  * Passwords hashed with bcrypt.
  * JWT-based authentication with expiration.
  * Token blacklisting to support logout.
* **Persistence**

  * SQLite database with SQLAlchemy ORM.
* **Role-Based Access Control**

  * Admins have elevated privileges.
  * Regular users are restricted to their own data.

---

## Technologies Used

* **FastAPI** – Modern Python API framework.
* **SQLAlchemy** – ORM for database handling.
* **SQLite** – Lightweight file-based database.
* **PyJWT** – JWT token handling.
* **passlib\[bcrypt]** – Password hashing.
* **python-multipart** – For form data parsing.
* **Uvicorn** – ASGI server.
* **Python 3.11+**

---

## Project Structure

```
Basic-Todo-Backend-Using-FastAPI/
├── controllers/
│   ├── auth.py          # Authentication logic
│   └── todo.py          # Todo CRUD logic
├── middleware/
│   └── auth.py          # JWT authentication middleware
├── models/
│   ├── todo.py          # Todo model and schemas
│   └── user.py          # User model and schemas
├── routes/
│   ├── auth.py          # Auth API routes
│   └── todo.py          # Todo API routes
├── database.py          # DB config and session management
├── main.py              # App initialization and routing
├── requirements.txt     # Python dependencies
└── todos.db             # SQLite database file
```

---

## Setup Instructions

1. Clone the repo:

   ```bash
   git clone <repository-url>
   cd Basic-Todo-Backend-Using-FastAPI
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:

   ```bash
   uvicorn main:app --reload
   ```

5. Open your browser and go to [http://localhost:8000/docs](http://localhost:8000/docs) to access the Swagger UI.

6. To check the database:

   ```bash
   sqlite3 todos.db
   .tables
   ```

   Should list `users` and `todos`.

---

## API Endpoints Summary

### Authentication (`/auth`)

| Method | Endpoint         | Description                  | Request Body                                                  | Response                                               |                                |
| ------ | ---------------- | ---------------------------- | ------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------ |
| POST   | `/auth/register` | Register new user            | \`{ "username": "string", "password": "string", "role": "user | admin" }\`                                             | User info (id, username, role) |
| POST   | `/auth/token`    | Login and get JWT token      | Form-data: username, password                                 | `{ "access_token": "string", "token_type": "bearer" }` |                                |
| POST   | `/auth/logout`   | Logout by blacklisting token | Auth header: Bearer `<token>`                                 | `{ "message": "Logged out successfully" }`             |                                |

### Todos (`/api`)

| Method | Endpoint         | Description                           | Request Body                                  | Response                                     |             |                     |
| ------ | ---------------- | ------------------------------------- | --------------------------------------------- | -------------------------------------------- | ----------- | ------------------- |
| POST   | `/api/`          | Create a new todo                     | \`{ "title": "string", "description": "string | null" }\`                                    | Todo object |                     |
| GET    | `/api/`          | Get all todos (admin: all, user: own) | Auth header                                   | List of Todo objects                         |             |                     |
| GET    | `/api/{todo_id}` | Get todo by ID                        | Auth header                                   | Todo object                                  |             |                     |
| PUT    | `/api/{todo_id}` | Update a todo                         | \`{ "title": "string                          | null", "description": "string                | null" }\`   | Updated Todo object |
| DELETE | `/api/{todo_id}` | Delete a todo (admin only)            | Auth header                                   | `{ "message": "Todo deleted successfully" }` |             |                     |

---

## Code Explanation

### Main Application (`main.py`)

Initializes FastAPI app, creates DB tables, includes routers, and defines root endpoint.

```python
from fastapi import FastAPI
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
```

---

### Database Configuration (`database.py`)

Sets up SQLite connection, session, and base model.

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

### User Model (`models/user.py`)

Defines SQLAlchemy and Pydantic user models with validation.

```python
from sqlalchemy import Column, Integer, String
from database import Base
from pydantic import BaseModel, Field, ConfigDict

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
```

---

### Todo Model (`models/todo.py`)

Defines SQLAlchemy and Pydantic todo models.

```python
from sqlalchemy import Column, Integer, String, DateTime
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
```

---

### Authentication Controller (`controllers/auth.py`)

Manages registration, login, logout, password hashing, and JWT token creation.

```python
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta
from models.user import User, UserCreate
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

def create_user
```


(user: UserCreate, db: Session):
db\_user = get\_user(user.username, db)
if db\_user:
raise HTTPException(status\_code=400, detail="Username already registered")
hashed\_password = hash\_password(user.password)
new\_user = User(username=user.username, password=hashed\_password, role=user.role)
db.add(new\_user)
db.commit()
db.refresh(new\_user)
return new\_user

def authenticate\_user(username: str, password: str, db: Session):
user = get\_user(username, db)
if not user:
return False
if not verify\_password(password, user.password):
return False
return user

def create\_access\_token(data: dict, expires\_delta: timedelta | None = None):
to\_encode = data.copy()
expire = datetime.utcnow() + (expires\_delta or timedelta(minutes=ACCESS\_TOKEN\_EXPIRE\_MINUTES))
to\_encode.update({"exp": expire})
encoded\_jwt = jwt.encode(to\_encode, SECRET\_KEY, algorithm=ALGORITHM)
return encoded\_jwt

def blacklist\_token(token: str):
blacklisted\_tokens.add(token)

def is\_token\_blacklisted(token: str) -> bool:
return token in blacklisted\_tokens

````

---

### Auth Routes (`routes/auth.py`)
Defines the authentication API routes.
```python
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from controllers.auth import (
    create_user,
    authenticate_user,
    create_access_token,
    blacklist_token,
    is_token_blacklisted,
)
from database import get_db
from models.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(user, db)

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = auth_header.removeprefix("Bearer ").strip()
    blacklist_token(token)
    return {"message": "Logged out successfully"}
````

---

### Middleware for JWT (`middleware/auth.py`)

Extracts and verifies JWT tokens on protected routes.

```python
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from controllers.auth import is_token_blacklisted
from models.user import User
from sqlalchemy.orm import Session
from database import get_db
from fastapi import Depends

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if is_token_blacklisted(credentials.credentials):
                raise HTTPException(status_code=403, detail="Token has been revoked.")
            try:
                payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
                username: str = payload.get("sub")
                role: str = payload.get("role")
                if username is None or role is None:
                    raise HTTPException(status_code=401, detail="Invalid token payload.")
                request.state.user = {"username": username, "role": role}
            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=401, detail="Token expired.")
            except jwt.PyJWTError:
                raise HTTPException(status_code=401, detail="Invalid token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

def get_current_user(request: Request = Depends()):
    return request.state.user
```

---

### Todo Controller (`controllers/todo.py`)

Manages CRUD operations with user access control.

```python
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.todo import Todo, TodoCreate, TodoUpdate

def get_all_todos(db: Session, username: str, role: str):
    if role == "admin":
        return db.query(Todo).all()
    return db.query(Todo).filter(Todo.username == username).all()

def get_todo_by_id(db: Session, todo_id: int):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

def create_todo(db: Session, todo_create: TodoCreate, username: str):
    todo = Todo(title=todo_create.title, description=todo_create.description, username=username)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

def update_todo(db: Session, todo_id: int, todo_update: TodoUpdate, username: str, role: str):
    todo = get_todo_by_id(db, todo_id)
    if todo.username != username and role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this todo")
    if todo_update.title is not None:
        todo.title = todo_update.title
    if todo_update.description is not None:
        todo.description = todo_update.description
    db.commit()
    db.refresh(todo)
    return todo

def delete_todo(db: Session, todo_id: int, username: str, role: str):
    todo = get_todo_by_id(db, todo_id)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete todos")
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}
```

---

### Todo Routes (`routes/todo.py`)

Defines API endpoints with authentication.

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from middleware.auth import JWTBearer, get_current_user
from database import get_db
from controllers.todo import get_all_todos, get_todo_by_id, create_todo, update_todo, delete_todo
from models.todo import TodoCreate, TodoUpdate, TodoResponse

router = APIRouter(dependencies=[Depends(JWTBearer())])

@router.get("/", response_model=list[TodoResponse])
def read_todos(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_all_todos(db, user["username"], user["role"])

@router.get("/{todo_id}", response_model=TodoResponse)
def read_todo(todo_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    todo = get_todo_by_id(db, todo_id)
    if todo.username != user["username"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this todo")
    return todo

@router.post("/", response_model=TodoResponse)
def create_new_todo(todo: TodoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return create_todo(db, todo, user["username"])

@router.put("/{todo_id}", response_model=TodoResponse)
def update_existing_todo(todo_id: int, todo_update: TodoUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return update_todo(db, todo_id, todo_update, user["username"], user["role"])

@router.delete("/{todo_id}")
def delete_existing_todo(todo_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return delete_todo(db, todo_id, user["username"], user["role"])
```

---

## Usage

* Register a new user with `POST /auth/register`.
* Login via `POST /auth/token` to get JWT token.
* Use the token in `Authorization: Bearer <token>` header to access todo routes.
* Admin users can view all todos and delete any todo.
* Regular users can manage only their own todos.

---

## Testing

* Use [Swagger UI](http://localhost:8000/docs) for easy manual testing.
* Use tools like Postman or curl for API testing.
* Add unit tests with `pytest` and `fastapi.testclient` for automated testing.

---

## Notes for Production

* Use environment variables or a secrets manager for sensitive keys.
* Use a production-grade database instead of SQLite (e.g., PostgreSQL).
* Implement token refresh mechanism.
* Add rate limiting and logging.
* Deploy with proper ASGI server like Gunicorn + Uvicorn workers.

---

## Contributing

Feel free to open issues or pull requests for improvements.
