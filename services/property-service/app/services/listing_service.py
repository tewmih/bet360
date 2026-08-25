from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional, Dict, Any, List

from app.repositories import ListingRepository
from app.schemas import CreateListingRequest, ListingResponse, LocationSchema, PricingSchema, PropertyDetailsSchema
from app.core.logging import logger
from app.core.exceptions import ListingPermissionError, ListingStatusError, ListingNotFoundError, ValidationError
from app.models.listing import Listing


class ListingService:
    """Service for listing business logic."""

    def __init__(self, db: AsyncSession, current_user_id: Optional[UUID] = None):
        self.db = db
        self.repo = ListingRepository(db)
        self.current_user_id = current_user_id

    def _get_user_id(self) -> UUID:
        """Get the current user ID or raise an error."""
        if not self.current_user_id:
            raise ListingPermissionError("User not authenticated")
        return self.current_user_id

    async def create_listing(self, data: CreateListingRequest, owner_id: UUID) -> ListingResponse:
        """Create a new listing."""
        # Validate pricing
        if data.pricing.amount <= 0:
            raise ValidationError("Monthly rent must be greater than 0", field="pricing.amount")
        
        # Validate location
        if not data.location.sub_city:
            raise ValidationError("Sub-city is required", field="location.sub_city")

        # Prepare listing data
        listing_data = {
            "owner_id": owner_id,
            "title": data.title,
            "description": data.description,
            "location": data.location.model_dump(),
            "pricing": data.pricing.model_dump(),
            "property_details": data.property_details.model_dump() if data.property_details else None,
            "status": "draft",
            "verification_status": "pending",
            "view_count": 0,
        }

        # Create listing
        listing = await self.repo.create(listing_data)
        logger.info(f"Listing created: {listing.id} for owner {owner_id}")
        
        return self._to_response(listing)  # ← FIXED

    async def get_listing(self, listing_id: UUID) -> ListingResponse:
        """Get listing by ID."""
        listing = await self.repo.get_by_id(listing_id)
        if not listing:
            logger.warning(f"Listing with ID {listing_id} not found")
            raise ListingNotFoundError(f"Listing with ID {listing_id} not found")
        return self._to_response(listing)

    async def get_my_listings(self, skip:  int = 0, limit: int = 20) -> List[ListingResponse]:
        """Get all listings for the current user."""
        owner_id = self._get_user_id()  # ← FIXED (single underscore)
        listings = await self.repo.get_by_owner(owner_id, skip=skip, limit=limit)
        return [self._to_response(listing) for listing in listings]

    async def update_listing(self, listing_id: UUID, data: Dict[str, Any]) -> ListingResponse:  # ← FIXED (method name)
        """Update a listing."""
        owner_id = self._get_user_id()

        # Get and validate listing
        listing = await self.repo.get_by_id(listing_id)
        if not listing:
            logger.warning(f"Listing with ID {listing_id} not found")
            raise ListingNotFoundError(f"Listing with ID {listing_id} not found")

        # Verify owner permission
        if listing.owner_id != owner_id:
            raise ListingPermissionError(f"You are not the owner of this listing (ID: {listing_id})")

        # Check status (only draft listings can be updated)
        if listing.status != "draft":
            raise ListingStatusError(f"Cannot edit listing in '{listing.status}' status")

        # Update the listing
        updated_listing = await self.repo.update(listing_id, data)

        if not updated_listing:
            raise ListingNotFoundError(f"Listing with ID {listing_id} not found")

        logger.info(f"Listing updated: {listing_id} by owner: {owner_id}")
        return self._to_response(updated_listing)

    async def delete_listing(self, listing_id: UUID) -> bool:  # ← FIXED (return type)
        """Delete a listing."""
        owner_id = self._get_user_id()

        # Get and validate listing
        listing = await self.repo.get_by_id(listing_id)
        if not listing:
            logger.warning(f"Listing with ID {listing_id} not found")
            raise ListingNotFoundError(f"Listing with ID {listing_id} not found")

        # Verify owner permission
        if listing.owner_id != owner_id:
            raise ListingPermissionError(f"You are not the owner of this listing (ID: {listing_id})")

        # Check status (only draft listings can be deleted)
        if listing.status != "draft":
            raise ListingStatusError(f"Cannot delete listing in '{listing.status}' status")
        
        return await self.repo.delete(listing_id)

    async def search_listings(
        self,
        city: Optional[str] = None,
        sub_city: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        bedrooms: Optional[int] = None,
        bathrooms: Optional[int] = None,
        property_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[ListingResponse], int]:
        """Search with filters."""
        listings, total = await self.repo.search(
            city=city,
            sub_city=sub_city,
            min_price=min_price,
            max_price=max_price,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            property_type=property_type,
            status="published",
            skip=skip,
            limit=limit,
        )
        return [self._to_response(listing) for listing in listings], total

    def _to_response(self, listing: Listing) -> ListingResponse:
        """Convert Listing model to ListingResponse schema."""
        return ListingResponse(
            id=listing.id,
            owner_id=listing.owner_id,
            title=listing.title,
            description=listing.description,
            location=LocationSchema(**listing.location),
            pricing=PricingSchema(**listing.pricing),
            property_details=PropertyDetailsSchema(**listing.property_details) if listing.property_details else None,
            status=listing.status,
            verification_status=listing.verification_status,
            published_at=listing.published_at,
            expires_at=listing.expires_at,
            view_count=listing.view_count,
            created_at=listing.created_at,
            updated_at=listing.updated_at,
        )