import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging

try:
    from .models import User, UserRole
    from .database import get_users_collection
except ImportError:
    from models import User, UserRole
    from database import get_users_collection

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()

class AuthError(Exception):
    """Custom authentication error"""
    pass

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")
    except jwt.JWTError:
        raise AuthError("Invalid token")

async def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email from database"""
    try:
        users_collection = await get_users_collection()
        user_data = await users_collection.find_one({"email": email})
        
        if user_data:
            return User(**user_data)
        return None
        
    except Exception as e:
        logger.error(f"Error fetching user by email: {e}")
        return None

async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID from database"""
    try:
        from bson import ObjectId
        users_collection = await get_users_collection()
        user_data = await users_collection.find_one({"_id": ObjectId(user_id)})
        
        if user_data:
            return User(**user_data)
        return None
        
    except Exception as e:
        logger.error(f"Error fetching user by ID: {e}")
        return None

async def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = await get_user_by_email(email)
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    # Update last login
    try:
        users_collection = await get_users_collection()
        await users_collection.update_one(
            {"_id": user.id},
            {"$set": {"last_login": datetime.utcnow()}}
        )
    except Exception as e:
        logger.error(f"Error updating last login: {e}")
    
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        # Check token type
        if payload.get("type") != "access":
            raise AuthError("Invalid token type")
        
        user_id = payload.get("sub")
        if user_id is None:
            raise AuthError("Invalid token payload")
        
        user = await get_user_by_id(user_id)
        if user is None:
            raise AuthError("User not found")
        
        return user
        
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_role(allowed_roles: list):
    """Decorator to require specific roles"""
    def decorator(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return decorator

# Role-based dependencies
async def get_current_police_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and ensure they have police role"""
    if current_user.role != UserRole.POLICE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Police role required"
        )
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and ensure they have admin role"""
    if current_user.role != UserRole.TOURISM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tourism admin role required"
        )
    return current_user

async def get_current_admin_or_police_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and ensure they have admin or police role"""
    if current_user.role not in [UserRole.POLICE, UserRole.TOURISM_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Police or admin role required"
        )
    return current_user