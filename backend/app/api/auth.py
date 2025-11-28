"""
Authentication API Endpoints Module

This module provides REST API endpoints for user authentication and management:
- User registration (with role-based setup)
- User login (JWT token generation)
- User information retrieval
- User logout

Features:
- Role-based user creation (admin, institution, student)
- Automatic ECDSA key pair generation for institutions
- Password hashing and validation
- JWT token-based authentication
- Input validation and error handling
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from ..database import get_db
from ..models.db_models import User, InstitutionKey
from ..utils.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..utils.ecdsa_utils import generate_key_pair

# ============================================================================
# API Router Setup
# ============================================================================

# Create router with prefix and tag for API documentation
router = APIRouter(prefix="/auth", tags=["authentication"])

# ============================================================================
# Pydantic Models for Request/Response Validation
# ============================================================================

class UserCreate(BaseModel):
    """
    Request model for user registration.
    
    Fields:
        username: Unique username for the user
        email: Valid email address (validated by EmailStr)
        password: Plain text password (will be hashed)
        role: User role - "admin", "institution", or "student" (default: "student")
        issuer_id: Required for institutions - unique identifier for the institution
        issuer_name: Required for institutions - name of the institution
    """
    username: str
    email: EmailStr
    password: str
    role: str = "student"  # admin, institution, student
    issuer_id: Optional[str] = None
    issuer_name: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def validate_and_truncate_password(cls, v: str) -> str:
        """
        Validate and truncate password to meet bcrypt's 72-byte limit.
        
        Bcrypt has a hard 72-byte limit. This validator:
        1. Checks minimum length (6 characters)
        2. Truncates to 72 bytes if longer (handles multi-byte UTF-8 characters)
        3. Ensures valid UTF-8 after truncation
        """
        if not v:
            raise ValueError("Password cannot be empty")
        
        # Check minimum length
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        
        # Convert to bytes to check actual byte length (handles UTF-8 multi-byte chars)
        password_bytes = v.encode('utf-8')
        
        # If password exceeds 72 bytes, truncate it
        if len(password_bytes) > 72:
            # Truncate to 72 bytes
            password_bytes = password_bytes[:72]
            # Decode back to string, handling potential incomplete UTF-8 sequences
            v = password_bytes.decode('utf-8', errors='ignore')
            # Ensure we have valid UTF-8 by trying to encode again
            try:
                v.encode('utf-8')
            except UnicodeEncodeError:
                # If still invalid, take first 71 bytes
                password_bytes = password_bytes[:71]
                v = password_bytes.decode('utf-8', errors='ignore')
        
        return v

class UserResponse(BaseModel):
    """
    Response model for user information.
    
    This model defines what user data is returned to clients.
    Sensitive fields like password hash are excluded.
    """
    id: int
    username: str
    email: str
    role: str
    issuer_id: Optional[str] = None
    issuer_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True  # Allow creation from SQLAlchemy models

class Token(BaseModel):
    """
    Response model for authentication tokens.
    
    Fields:
        access_token: JWT token string for API authentication
        token_type: Always "bearer" for OAuth2 compatibility
    """
    access_token: str
    token_type: str

# ============================================================================
# Registration Endpoint
# ============================================================================

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    This endpoint creates a new user account with the specified role.
    For institutions, it also generates an ECDSA key pair for certificate signing.
    
    Process:
    1. Validate username and email are unique
    2. Validate role is valid
    3. For institutions, validate issuer_id and issuer_name are provided
    4. Hash the password
    5. Create user record in database
    6. For institutions, generate and store ECDSA key pair
    7. Return user information (without password)
    
    Args:
        user_data: User registration data (username, email, password, role, etc.)
        db: Database session (injected by FastAPI)
    
    Returns:
        UserResponse: Created user information
    
    Raises:
        HTTPException: 400 if validation fails (duplicate username/email, invalid role, etc.)
    """
    # ========================================================================
    # Validation: Check for duplicate username
    # ========================================================================
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # ========================================================================
    # Validation: Check for duplicate email
    # ========================================================================
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # ========================================================================
    # Validation: Check role is valid
    # ========================================================================
    if user_data.role not in ["admin", "institution", "student"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be admin, institution, or student"
        )
    
    # ========================================================================
    # Validation: Institutions must provide issuer information
    # ========================================================================
    if user_data.role == "institution":
        if not user_data.issuer_id or not user_data.issuer_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Institutions must provide issuer_id and issuer_name"
            )
        # Check if issuer_id already exists (must be unique)
        existing_issuer = db.query(User).filter(
            User.issuer_id == user_data.issuer_id
        ).first()
        if existing_issuer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Issuer ID already registered"
            )
    
    # ========================================================================
    # Create User Record
    # ========================================================================
    # Note: Password validation and truncation is handled by Pydantic validator
    # The password is already validated and truncated to 72 bytes if needed
    # Hash password before storing (never store plain text passwords!)
    try:
        hashed_password = get_password_hash(user_data.password)
    except ValueError as e:
        # Handle password validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password error: {str(e)}"
        )
    except Exception as e:
        # Handle bcrypt/passlib compatibility issues
        error_msg = str(e)
        if "bcrypt" in error_msg.lower() or "__about__" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Password hashing failed due to bcrypt version incompatibility. "
                    "Please reinstall bcrypt 3.2.2: pip uninstall bcrypt && pip install bcrypt==3.2.2"
                )
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password hashing error: {error_msg}"
        )
    
    # Create new user object
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        issuer_id=user_data.issuer_id,
        issuer_name=user_data.issuer_name
    )
    
    # Add to database session
    db.add(new_user)
    db.flush()  # Flush to get the user ID
    
    # ========================================================================
    # Generate ECDSA Key Pair for Institutions
    # ========================================================================
    # Institutions need key pairs to sign certificates
    if user_data.role == "institution":
        key_pair = generate_key_pair()
        institution_key = InstitutionKey(
            user_id=new_user.id,
            issuer_id=user_data.issuer_id,
            private_key_encrypted=key_pair['private_key'],  # In production, encrypt this!
            public_key=key_pair['public_key']
        )
        db.add(institution_key)
    
    # ========================================================================
    # Commit Transaction
    # ========================================================================
    db.commit()
    db.refresh(new_user)  # Refresh to get database-generated fields
    
    return new_user

# ============================================================================
# Login Endpoint
# ============================================================================

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT access token.
    
    This endpoint validates user credentials and returns a JWT token
    that can be used for authenticated API requests.
    
    Process:
    1. Look up user by username
    2. Verify password against stored hash
    3. Check if user account is active
    4. Generate JWT token with user information
    5. Return token to client
    
    Args:
        form_data: OAuth2 password form (username and password)
        db: Database session (injected by FastAPI)
    
    Returns:
        Token: JWT access token and token type
    
    Raises:
        HTTPException: 401 if credentials are invalid
        HTTPException: 400 if user account is inactive
    """
    # ========================================================================
    # Look Up User
    # ========================================================================
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # ========================================================================
    # Verify Credentials
    # ========================================================================
    # Check if user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ========================================================================
    # Check Account Status
    # ========================================================================
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # ========================================================================
    # Generate JWT Token
    # ========================================================================
    # Create token with user information and expiration
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Return token in OAuth2 format
    return {"access_token": access_token, "token_type": "bearer"}

# ============================================================================
# Current User Information Endpoint
# ============================================================================

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get information about the currently authenticated user.
    
    This endpoint requires authentication (JWT token in Authorization header).
    It returns the user's information based on the token.
    
    Args:
        current_user: Authenticated user (from get_current_user dependency)
    
    Returns:
        UserResponse: Current user's information
    """
    return current_user

# ============================================================================
# Logout Endpoint
# ============================================================================

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout endpoint for explicit logout.
    
    Note: With JWT tokens, logout is primarily handled client-side by removing
    the token from storage. This endpoint provides a way to explicitly log out
    and can be extended in the future to support token blacklisting if needed.
    
    In a production system with token blacklisting:
    - Store token in a blacklist (Redis, database)
    - Check blacklist on each authenticated request
    - Reject requests with blacklisted tokens
    
    Args:
        current_user: Authenticated user (from get_current_user dependency)
    
    Returns:
        dict: Logout confirmation message
    """
    return {
        "message": "Logged out successfully",
        "detail": "Token should be removed from client storage"
    }
