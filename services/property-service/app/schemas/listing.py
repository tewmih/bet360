from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


# Location Schema
class LocationSchema(BaseModel):
    country: str = Field(default="Ethiopia")
    city: str = Field(default="Addis Ababa")
    sub_city: str
    wereda: Optional[str] = None
    neighborhood: Optional[str] = None
    address_line: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


# Pricing Schema
class PricingSchema(BaseModel):
    amount: int = Field(gt=0, description="Monthly rent in ETB")
    currency: str = Field(default="ETB")
    negotiable: bool = Field(default=False)
    deposit_required: bool = Field(default=False)
    deposit_amount: Optional[int] = Field(None, gt=0)

    @field_validator("deposit_amount")
    def validate_deposit(cls, v, values):
        if values.data.get("deposit_required") and v is None:
            raise ValueError("Deposit amount is required when deposit is required")
        return v


# Property Details Schema
class PropertyDetailsSchema(BaseModel):
    property_type: str = Field(..., description="apartment, house, condo, studio, villa, townhouse")
    bedrooms: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[int] = Field(None, ge=0)
    area_sqm: Optional[int] = Field(None, gt=0)
    furnishing_status: Optional[str] = Field(None, description="furnished, semi_furnished, unfurnished")
    floor_number: Optional[int] = Field(None, ge=0)
    total_floors: Optional[int] = Field(None, ge=0)
    parking_available: bool = Field(default=False)
    pet_friendly: bool = Field(default=False)
    year_built: Optional[int] = Field(None, ge=1900)


# Create Listing Request
class CreateListingRequest(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    location: LocationSchema
    pricing: PricingSchema
    property_details: Optional[PropertyDetailsSchema] = None


# Listing Response
class ListingResponse(BaseModel):
    id: UUID
    owner_id: UUID
    title: str
    description: Optional[str]
    location: LocationSchema
    pricing: PricingSchema
    property_details: Optional[PropertyDetailsSchema]
    status: str
    verification_status: str
    published_at: Optional[datetime]
    expires_at: Optional[datetime]
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Listings Response (for search)
class ListingsResponse(BaseModel):
    items: List[ListingResponse]
    total: int
    page: int
    limit: int
    total_pages: int