"""
Authentication and security utilities for JWT and password hashing.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import jwt, JWTError
import bcrypt
import os


def hash_password(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    Bcrypt limits passwords to 72 bytes, so we handle that constraint.
    """
    password_bytes = password.encode('utf-8')
    # bcrypt limits to 72 bytes
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_jwt(
    data: Dict[str, Any],
    secret: str = None,
    minutes: int = None,
    algorithm: str = None
) -> str:
    """
    Create a JWT token with the given data.
    
    Args:
        data: Dictionary to encode in the token
        secret: JWT secret (defaults to env var JWT_SECRET)
        minutes: Token expiry in minutes (defaults to env var JWT_EXPIRY_MINUTES)
        algorithm: JWT algorithm (defaults to env var JWT_ALGORITHM)
    """
    secret = secret or os.getenv('JWT_SECRET', 'dev-secret-change-in-production')
    minutes = minutes or int(os.getenv('JWT_EXPIRY_MINUTES', '1440'))
    algorithm = algorithm or os.getenv('JWT_ALGORITHM', 'HS256')
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    to_encode['exp'] = expire
    
    return jwt.encode(to_encode, secret, algorithm=algorithm)


def decode_jwt(
    token: str,
    secret: str = None,
    algorithm: str = None
) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token string
        secret: JWT secret (defaults to env var JWT_SECRET)
        algorithm: JWT algorithm (defaults to env var JWT_ALGORITHM)
        
    Returns:
        Decoded token payload or None if invalid
    """
    secret = secret or os.getenv('JWT_SECRET', 'dev-secret-change-in-production')
    algorithm = algorithm or os.getenv('JWT_ALGORITHM', 'HS256')
    
    try:
        return jwt.decode(token, secret, algorithms=[algorithm])
    except JWTError:
        return None
