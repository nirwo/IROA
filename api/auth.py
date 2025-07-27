"""
Authentication and Authorization Module for IROA System
Provides JWT token management, password hashing, and role-based access control
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # Generate a secure random secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token scheme
security = HTTPBearer()

# User roles
class UserRole:
    ADMIN = "admin"
    USER = "user"

# Pydantic models
class User(BaseModel):
    username: str
    email: Optional[str] = None
    role: str = UserRole.USER
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    role: str = UserRole.USER

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: User

# In-memory user storage (in production, use a proper database)
users_db: Dict[str, UserInDB] = {}

# Initialize with default admin user
def init_default_users():
    """Initialize system with default admin and demo users"""
    if not users_db:
        # Create default admin user
        admin_user = UserInDB(
            username="admin",
            email="admin@iroa.local",
            role=UserRole.ADMIN,
            is_active=True,
            created_at=datetime.now(),
            hashed_password=get_password_hash("admin123")
        )
        users_db["admin"] = admin_user
        
        # Create demo regular user
        demo_user = UserInDB(
            username="user",
            email="user@iroa.local", 
            role=UserRole.USER,
            is_active=True,
            created_at=datetime.now(),
            hashed_password=get_password_hash("user123")
        )
        users_db["user"] = demo_user
        
        print("🔐 Initialized default users:")
        print("   Admin: admin/admin123 (full access)")
        print("   User:  user/user123 (limited access)")

# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

# User management
def get_user(username: str) -> Optional[UserInDB]:
    """Get user by username"""
    return users_db.get(username)

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate user with username and password"""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user

def create_user(user_data: UserCreate) -> UserInDB:
    """Create a new user"""
    if user_data.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    hashed_password = get_password_hash(user_data.password)
    user = UserInDB(
        username=user_data.username,
        email=user_data.email,
        role=user_data.role,
        is_active=True,
        created_at=datetime.now(),
        hashed_password=hashed_password
    )
    users_db[user_data.username] = user
    return user

# JWT token management
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None

# Authentication dependencies
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = get_user(username)
    if user is None:
        raise credentials_exception
    
    # Update last login
    user.last_login = datetime.now()
    
    # Return User model (without password)
    return User(
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login
    )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require admin role for access"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Optional authentication (allows both authenticated and anonymous access)
async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    """Get current user if authenticated, None if not"""
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            return None
        
        username: str = payload.get("sub")
        if username is None:
            return None
            
        user = get_user(username)
        if user is None or not user.is_active:
            return None
        
        # Update last login
        user.last_login = datetime.now()
        
        return User(
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
    except:
        return None

# Role-based access control helpers
def check_admin_access(user: Optional[User]) -> bool:
    """Check if user has admin access"""
    return user is not None and user.role == UserRole.ADMIN

def check_user_access(user: Optional[User]) -> bool:
    """Check if user has at least user access"""
    return user is not None and user.is_active

def get_user_permissions(user: Optional[User]) -> Dict[str, bool]:
    """Get user permissions for frontend"""
    if not user:
        return {
            "can_view_dashboard": False,
            "can_view_profile_preview": False,
            "can_view_vms": False,
            "can_view_analytics": False,
            "can_view_capacity_planner": False,
            "can_view_license_management": False,
            "can_view_administration": False,
            "can_configure_system": False,
            "can_manage_users": False
        }
    
    if user.role == UserRole.ADMIN:
        return {
            "can_view_dashboard": True,
            "can_view_profile_preview": True,
            "can_view_vms": True,
            "can_view_analytics": True,
            "can_view_capacity_planner": True,
            "can_view_license_management": True,
            "can_view_administration": True,
            "can_configure_system": True,
            "can_manage_users": True
        }
    else:  # Regular user
        return {
            "can_view_dashboard": True,
            "can_view_profile_preview": True,
            "can_view_vms": False,
            "can_view_analytics": False,
            "can_view_capacity_planner": False,
            "can_view_license_management": False,
            "can_view_administration": False,
            "can_configure_system": False,
            "can_manage_users": False
        }

# Initialize default users on module import
init_default_users()
