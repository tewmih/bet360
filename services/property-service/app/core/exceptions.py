from typing import Optional, Any
from uuid import UUID

class PropertyServiceExceptions(Exception):
    """All exceptions of property service"""

    def __init__(
        self,
        messgae: str,
        code: Optional[str] = None,
        field: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        self.messgae = messgae
        self.code = code or self.__class__.__name__
        self.field = field
        self.details = details
        super().__init__(messgae)
        

class ListingNotFoundError(PropertyServiceExceptions):
        """Raised when a listing is not found."""
        def __init__(self, listing_id: Optional[str] = None):
            message = f"Listing with ID '{listing_id}' not found" if listing_id else "Listing not found"
            super().__init__(messgae=message, code="LISTING_NOT_FOUND")

class ListingPermissionError(PropertyServiceExceptions):
         """Raised when a user doesn't have permission to access a listing."""
         def __init__(self, message: str = "You don't have permission to perform this action"):
            super().__init__(message, code="LISTING_PERMISSION_DENIED")
    

class ListingStatusError(PropertyServiceExceptions):
        """Raised when an operation can't be performed due to listing status."""
        def __init__(self, message: str):
            super().__init__(message, code="LISTING_STATUS_ERROR")
    
    
class ValidationError(PropertyServiceExceptions):
        """Raised when data validation fails."""
        def __init__(self, message: str, field: Optional[str] = None):
            super().__init__(message, code="VALIDATION_ERROR", field=field)


class AuthenticationError(PropertyServiceExceptions):
    """Raised when a user is not authenticated."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, code="AUTHENTICATION_REQUIRED")


class OwnerVerificationError(PropertyServiceExceptions):
    """Raised when an owner is not verified."""
    
    def __init__(self, message: str = "Owner must be verified to publish listings"):
        super().__init__(message, code="OWNER_NOT_VERIFIED")


class DuplicateListingError(PropertyServiceExceptions):
    """Raised when a duplicate listing is detected."""
    
    def __init__(self, message: str = "A duplicate listing already exists for this property"):
        super().__init__(message, code="DUPLICATE_LISTING")