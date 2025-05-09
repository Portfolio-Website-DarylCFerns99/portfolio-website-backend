from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from jose import JWTError
from app.dependencies.database import get_db
from app.models.user_model import User
from app.security.token import decode_token
from typing import Optional
import uuid
import logging
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

security = HTTPBearer()

async def get_current_user(
    authorization: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current user based on the JWT token in the authorization header.
    
    Raises HTTPException if token is invalid or user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not authorization:
        raise credentials_exception
    
    try:
        # Extract token from authorization header (Bearer token)
        scheme, token = authorization.scheme, authorization.credentials
        if scheme.lower() != "bearer":
            raise credentials_exception
        
        # Decode the token
        payload = decode_token(token)
        user_id_str = payload.get("sub")
        
        if user_id_str is None:
            raise credentials_exception
        
        # Convert string to UUID
        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise credentials_exception
        
    except (JWTError, ValueError) as e:
        logger.error(f"Token validation error: {str(e)}")
        raise credentials_exception
    
    # Get the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
    
    return user
