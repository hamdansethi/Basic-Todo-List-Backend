from fastapi import HTTPException  # Used to show error messages when something goes wrong
from passlib.context import CryptContext  # Helps us hash (scramble) passwords to keep them safe
from sqlalchemy.orm import Session  # Lets us talk to the database
import jwt  # Used to create and read secret login tokens (JWTs)
from datetime import datetime, timedelta  # Helps us manage time (like token expiration)
from models.user import User, UserCreate  # Our user data models (like blueprints for making users)
from database import get_db  # Function to get the database connection
from typing import Set  # A special kind of collection to keep track of blacklisted tokens

# Secret key used to sign tokens (should be long and hard to guess)
SECRET_KEY = "your-secret-key"  # ⚠️ Change this to something secure in real apps

# The algorithm used to create the token
ALGORITHM = "HS256"

# Token will expire after 30 minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Setting up the password hasher using bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# A set to keep track of tokens that are no longer valid (like after logout)
blacklisted_tokens: Set[str] = set()

# Check if the given password matches the hashed password in the database
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Turn a plain password into a hashed (scrambled) version
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Get a user from the database by their username
def get_user(username: str, db: Session):
    return db.query(User).filter(User.username == username).first()

# Create a new user if the username doesn't already exist
def create_user(user: UserCreate, db: Session):
    if get_user(user.username, db):
        raise HTTPException(status_code=400, detail="Username already exists")  # Show error if taken
    hashed_password = hash_password(user.password)  # Hash the password before storing
    db_user = User(username=user.username, password=hashed_password, role=user.role)  # Create user object
    db.add(db_user)  # Add user to database
    db.commit()  # Save changes
    db.refresh(db_user)  # Get the latest user data from the database
    return db_user  # Return the new user

# Check if the user exists and if the password is correct
def authenticate_user(username: str, password: str, db: Session):
    user = get_user(username, db)  # Get the user from the database
    if not user or not verify_password(password, user.password):
        return False  # Return False if no user or wrong password
    return user  # Return the user if login is correct

# Create a token for the user with an expiration time
def create_access_token(data: dict):
    to_encode = data.copy()  # Copy the data to encode
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Set expire time
    to_encode.update({"exp": expire})  # Add expire time to token data
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Create the token
    return encoded_jwt  # Return the token

# Add a token to the blacklist (used for logout)
def blacklist_token(token: str):
    blacklisted_tokens.add(token)

# Check if a token has been blacklisted
def is_token_blacklisted(token: str) -> bool:
    return token in blacklisted_tokens
