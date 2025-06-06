from fastapi import Depends, HTTPException, status  # For dependency injection and error handling
from fastapi.security import OAuth2PasswordBearer   # Helps extract the token from the request
import jwt  # To decode and verify JWT tokens
from controllers.auth import SECRET_KEY, ALGORITHM, get_user, is_token_blacklisted  # Reused auth functions/constants
from sqlalchemy.orm import Session  # Database session
from database import get_db  # Dependency to get DB session
from models.user import User  # User model for type hinting

# OAuth2 scheme that looks for the Bearer token in the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Function to get the current logged-in user from the token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # This is the default error we'll return if something goes wrong
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # First, check if the token is blacklisted (user logged out)
    if is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token is invalid (logged out)")

    try:
        # Try to decode the token using our secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # 'sub' usually holds the username
        if username is None:
            raise credentials_exception  # If no username in token, throw error
    except jwt.PyJWTError:
        raise credentials_exception  # If token is invalid or expired, throw error

    # Use the username to get the actual user from the database
    user = get_user(username, db)
    if user is None:
        raise credentials_exception  # If user not found, throw error
    return user  # Return the current user object

# Function to restrict access to only admin users
def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":  # Check if the user's role is admin
        raise HTTPException(status_code=403, detail="Not enough permissions")  # Forbidden if not admin
    return current_user  # Return the admin user
