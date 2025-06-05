from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta
from models.user import User, UserCreate
from database import get_db
from typing import Set

SECRET_KEY = "your-secret-key"  # Change to secure random string
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