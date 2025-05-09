from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from app.config.settings import settings
import os
import logging
import uuid

logger = logging.getLogger(__name__)

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "YOUR_DEFAULT_SECRET_KEY_CHANGE_THIS")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token and return the payload.
    Raises JWTError if token is invalid.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
