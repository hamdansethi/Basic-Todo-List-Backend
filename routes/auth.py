from fastapi import APIRouter, Depends, HTTPException, status  # FastAPI utilities
from fastapi.security import OAuth2PasswordRequestForm  # For handling form-based login
from sqlalchemy.orm import Session  # For DB session handling
from controllers.auth import authenticate_user, create_access_token, create_user, blacklist_token  # Controller functions
from models.user import UserCreate, UserResponse  # Pydantic models
from database import get_db  # DB session dependency
from pydantic import BaseModel  # BaseModel for response schema
from middleware.auth import oauth2_scheme  # Token extractor middleware

router = APIRouter()  # Creating a router instance to define routes

# Schema for the token response (used after login)
class Token(BaseModel):
    access_token: str
    token_type: str

# Route to register a new user
@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(user, db)  # Create a new user in DB
    return db_user  # Return newly created user details (without password)

# Route to log in and receive a JWT token
@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)  # Verify user credentials
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",  # Return unauthorized error
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Generate access token with user's username and role
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}  # Return token

# Route to logout by blacklisting the token
@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    blacklist_token(token)  # Add token to blacklist
    return {"message": "Logged out successfully"}  # Confirmation message
