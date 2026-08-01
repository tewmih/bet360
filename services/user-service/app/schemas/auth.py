from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID
from datetime import datetime
import re

class RegisterRequest(BaseModel):
    """Request schema for user registration."""
    
    full_name: str = Field(..., min_length=2, max_length=255, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    phone_number: str = Field(..., description="User's phone number")
    password: str = Field(..., min_length=8, description="User's password (min 8 characters)")
    
    @validator('phone_number')
    def validate_phone(cls, v):
        """Validate phone number format."""
        # Remove common separators but keep + for country code
        cleaned = re.sub(r'[\s\-\(\)]', '', v)
        
        # Allow + at the beginning for country code
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]  # Remove + for digit check
            if not cleaned.isdigit():
                raise ValueError('Phone number must contain only digits, spaces, or hyphens, with optional + prefix')
        elif not cleaned.isdigit():
            raise ValueError('Phone number must contain only digits, spaces, or hyphens')
        
        if len(cleaned) < 9 or len(cleaned) > 15:
            raise ValueError('Phone number must be between 9 and 15 digits')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        # Optional: add more checks
        # if not re.search(r'[A-Z]', v):
        #     raise ValueError('Password must contain at least one uppercase letter')
        # if not re.search(r'[a-z]', v):
        #     raise ValueError('Password must contain at least one lowercase letter')
        # if not re.search(r'[0-9]', v):
        #     raise ValueError('Password must contain at least one number')
        return v

class RegisterResponse(BaseModel):
    """Response schema for user registration."""
    
    id: UUID
    full_name: str
    email: str
    phone_number: str
    role: str
    is_verified: bool
    is_active: bool
    trust_score: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Response schema for JWT tokens."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"