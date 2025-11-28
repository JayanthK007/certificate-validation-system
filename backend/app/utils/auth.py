"""
JWT Authentication Utilities Module

This module provides authentication and authorization functionality using JWT (JSON Web Tokens).
It includes:
- Password hashing and verification (bcrypt)
- JWT token creation and validation
- FastAPI dependencies for protecting routes
- Role-based access control (admin, institution, student)

Security Features:
- Bcrypt password hashing with salt
- JWT tokens with expiration
- Role-based authorization
- Token validation on every protected request
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.db_models import User

# ============================================================================
# Security Configuration
# ============================================================================

# Secret key for JWT token signing - MUST be changed in production!
# In production, use environment variable: os.getenv("SECRET_KEY")
SECRET_KEY = "your-secret-key-change-in-production-use-env-variable"

# JWT algorithm for token signing
ALGORITHM = "HS256"

# Token expiration time in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ============================================================================
# Password Hashing Configuration
# ============================================================================

# CryptContext for password hashing using bcrypt
# bcrypt automatically handles salt generation and is resistant to timing attacks
# Note: Using bcrypt 3.2.2 for compatibility with passlib 1.7.4
# IMPORTANT: Do not use bcrypt 4.x as it's incompatible with passlib 1.7.4
try:
    import bcrypt
    if hasattr(bcrypt, '__version__'):
        bcrypt_version = bcrypt.__version__
    elif hasattr(bcrypt, '__about__'):
        bcrypt_version = bcrypt.__about__.__version__
    else:
        bcrypt_version = "unknown"
    # Warn if wrong version
    if not bcrypt_version.startswith('3.'):
        import warnings
        warnings.warn(
            f"Warning: bcrypt version {bcrypt_version} detected. "
            "This may cause compatibility issues with passlib 1.7.4. "
            "Please install bcrypt==3.2.2: pip install bcrypt==3.2.2"
        )
except ImportError:
    pass

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Number of rounds for bcrypt (higher = more secure but slower)
)

# ============================================================================
# OAuth2 Password Bearer Scheme
# ============================================================================

# OAuth2 scheme for token extraction from Authorization header
# This tells FastAPI where to find the login endpoint for token generation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ============================================================================
# Password Utilities
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a bcrypt hash.
    
    This function uses bcrypt's constant-time comparison to prevent timing attacks.
    
    Args:
        plain_password: The password provided by the user (plain text)
        hashed_password: The stored password hash from the database
    
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Bcrypt automatically generates a salt and includes it in the hash.
    Each call produces a different hash even for the same password (due to salt).
    
    Note: Bcrypt has a 72-byte limit for passwords. Longer passwords are truncated.
    
    Args:
        password: Plain text password to hash (max 72 bytes)
    
    Returns:
        str: Bcrypt hash string (includes salt)
    
    Raises:
        ValueError: If password is empty or None
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    # CRITICAL: Bcrypt has a 72-byte limit
    # Truncate password BEFORE passing to passlib to avoid internal errors
    # Convert to bytes to check length accurately (handles multi-byte characters)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate to exactly 72 bytes
        password_bytes = password_bytes[:72]
        # Decode back to string, handling potential incomplete UTF-8 sequences
        password = password_bytes.decode('utf-8', errors='ignore')
        # If truncation broke a multi-byte character, remove the last character
        # to ensure we have a valid UTF-8 string
        try:
            password.encode('utf-8')
        except UnicodeEncodeError:
            # If still invalid, take first 71 bytes and try again
            password_bytes = password_bytes[:71]
            password = password_bytes.decode('utf-8', errors='ignore')
    
    # Now hash the (potentially truncated) password
    return pwd_context.hash(password)

# ============================================================================
# JWT Token Utilities
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    The token contains user information (username, role) and an expiration time.
    Tokens are signed with the secret key to prevent tampering.
    
    Args:
        data: Dictionary containing user data to encode in token (e.g., {"sub": username, "role": "institution"})
        expires_delta: Optional custom expiration time. If None, uses default ACCESS_TOKEN_EXPIRE_MINUTES
    
    Returns:
        str: Encoded JWT token string
    """
    # Copy data to avoid modifying the original
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add expiration to token payload
    to_encode.update({"exp": expire})
    
    # Encode and sign the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception) -> str:
    """
    Verify and decode a JWT token.
    
    This function validates the token signature and extracts the username.
    Raises an exception if the token is invalid, expired, or tampered with.
    
    Args:
        token: JWT token string from Authorization header
        credentials_exception: Exception to raise if token is invalid
    
    Returns:
        str: Username extracted from token payload
    
    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    try:
        # Decode and verify token signature
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract username from token payload (subject)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        return username
    except JWTError:
        # Token is invalid, expired, or tampered with
        raise credentials_exception

# ============================================================================
# FastAPI Dependencies for Route Protection
# ============================================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to get the current authenticated user.
    
    This dependency:
    1. Extracts the JWT token from the Authorization header
    2. Verifies the token signature and expiration
    3. Looks up the user in the database
    4. Returns the user object if valid
    
    Usage:
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.username}
    
    Args:
        token: JWT token extracted from Authorization header (via oauth2_scheme)
        db: Database session (injected by FastAPI)
    
    Returns:
        User: The authenticated user object from database
    
    Raises:
        HTTPException: 401 if token is invalid or user not found
        HTTPException: 400 if user account is inactive
    """
    # Exception to raise if authentication fails
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify token and extract username
    username = verify_token(token, credentials_exception)
    
    # Look up user in database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    # Check if user account is active
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user

async def get_current_active_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    FastAPI dependency to verify user is an admin.
    
    This dependency builds on get_current_user and adds an additional check
    to ensure the user has admin role. Used for admin-only endpoints.
    
    Usage:
        @router.delete("/admin-only")
        async def admin_endpoint(admin: User = Depends(get_current_active_admin)):
            # Only admins can access this
            pass
    
    Args:
        current_user: Authenticated user (from get_current_user dependency)
    
    Returns:
        User: The authenticated admin user
    
    Raises:
        HTTPException: 403 if user is not an admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_current_institution(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    FastAPI dependency to verify user is an institution or admin.
    
    This dependency ensures only institutions and admins can access certain endpoints
    (like issuing certificates). Used for institution-only operations.
    
    Usage:
        @router.post("/certificates/issue")
        async def issue_certificate(
            current_user: User = Depends(get_current_institution)
        ):
            # Only institutions and admins can issue certificates
            pass
    
    Args:
        current_user: Authenticated user (from get_current_user dependency)
    
    Returns:
        User: The authenticated institution or admin user
    
    Raises:
        HTTPException: 403 if user is not an institution or admin
    """
    if current_user.role not in ["admin", "institution"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only institutions and admins can issue certificates"
        )
    return current_user
