from typing import Optional, Any
from fastapi import HTTPException, status


class Bet360Exception(HTTPException):
    """Base exception for Bet360."""
    
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        field: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "code": code,
                "message": message,
                "field": field,
                "details": details,
            }
        )


class EmailAlreadyExistsError(Bet360Exception):
    """Raised when email is already registered."""
    
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="EMAIL_ALREADY_EXISTS",
            message=f"A user with email '{email}' already exists.",
            field="email",
        )


class PhoneAlreadyExistsError(Bet360Exception):
    """Raised when phone is already registered."""
    
    def __init__(self, phone: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="PHONE_ALREADY_EXISTS",
            message=f"A user with phone '{phone}' already exists.",
            field="phone_number",
        )


class InvalidCredentialsError(Bet360Exception):
    """Raised when credentials are invalid."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="INVALID_CREDENTIALS",
            message="Invalid email/phone or password.",
        )


class InvalidTokenError(Bet360Exception):
    """Raised when token is invalid or expired."""
    
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="INVALID_TOKEN",
            message=message,
        )


class RefreshTokenError(Bet360Exception):
    """Raised when refresh token is invalid."""
    
    def __init__(self, message: str = "Invalid or expired refresh token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="INVALID_REFRESH_TOKEN",
            message=message,
        )