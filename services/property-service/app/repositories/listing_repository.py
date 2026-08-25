from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_, and_, func, cast, Integer
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from typing import Optional, List, Dict, Any

from app.models.listing import Listing
from app.core.logging import logger


class ListingRepository:
    """Repository for Listing database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, listing_data: Dict[str, Any]) -> Listing:
        """Create a new listing."""
        try:
            listing = Listing(**listing_data)
            self.db.add(listing)
            await self.db.commit()
            await self.db.refresh(listing)
            logger.info(f"Listing created: {listing.id}, title: {listing.title}")
            return listing
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Integrity error creating listing: {e}")
            raise

    async def get_by_id(self, listing_id: UUID) -> Optional[Listing]:
        """Get a listing by ID."""
        result = await self.db.execute(
            select(Listing).where(Listing.id == listing_id)
        )
        listing = result.scalar_one_or_none()
        if listing:
            logger.debug(f"Listing retrieved: {listing_id}")
        else:
            logger.debug(f"Listing not found: {listing_id}")
        return listing

    async def get_by_owner(self, owner_id: UUID, skip: int = 0, limit: int = 20) -> List[Listing]:
        """Get all listings for an owner."""
        result = await self.db.execute(
            select(Listing)
            .where(Listing.owner_id == owner_id)
            .order_by(Listing.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        listings = list(result.scalars().all())
        logger.debug(f"Retrieved {len(listings)} listings for owner: {owner_id}")
        return listings

    async def update(self, listing_id: UUID, update_data: Dict[str, Any]) -> Optional[Listing]:
        """Update a listing."""
        listing = await self.get_by_id(listing_id)
        if not listing:
            logger.warning(f"Listing not found for update: {listing_id}")
            return None

        # Update fields
        for key, value in update_data.items():
            if hasattr(listing, key) and value is not None:
                setattr(listing, key, value)

        await self.db.commit()
        await self.db.refresh(listing)
        logger.info(f"Listing updated: {listing_id}")
        return listing

    async def delete(self, listing_id: UUID) -> bool:
        """Delete/archive a listing."""
        listing = await self.get_by_id(listing_id)

        if not listing:
            logger.warning(f"Listing with id: {listing_id} doesn't exist")
            return False

        await self.db.delete(listing)
        await self.db.commit()
        logger.info(f"Listing with id: {listing_id} deleted")
        return True

    async def search(
        self,
        city: Optional[str] = None,
        sub_city: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        bedrooms: Optional[int] = None,
        bathrooms: Optional[int] = None,
        property_type: Optional[str] = None,
        status: Optional[str] = "published",
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Listing], int]:
        """Search listings with filters."""
        query = select(Listing).where(Listing.status == status)

        # Filters
        if city:
            query = query.where(Listing.location["city"].astext.ilike(f"%{city}%"))

        if sub_city:
            query = query.where(Listing.location["sub_city"].astext.ilike(f"%{sub_city}%"))

        if min_price is not None:
            query = query.where(cast(Listing.pricing["amount"].astext, Integer) >= min_price)

        if max_price is not None:
            query = query.where(cast(Listing.pricing["amount"].astext, Integer) <= max_price)

        if bedrooms is not None:
            query = query.where(cast(Listing.property_details["bedrooms"].astext, Integer) == bedrooms)

        if bathrooms is not None:
            query = query.where(cast(Listing.property_details["bathrooms"].astext, Integer) == bathrooms)

        if property_type:
            query = query.where(Listing.property_details["property_type"].astext == property_type)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.order_by(Listing.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        listings = list(result.scalars().all())

        logger.debug(f"Search returned {len(listings)} listings out of {total}")
        return listings, total