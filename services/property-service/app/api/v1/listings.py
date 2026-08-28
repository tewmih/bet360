from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional, List, Dict

from app.db.session import get_db
from app.services.listing_service import ListingService
from app.schemas.listing import CreateListingRequest, ListingResponse, ListingsResponse, UpdateListingRequest
from app.core.logging import logger
from app.core.exceptions import (
    ListingNotFoundError,
    ListingPermissionError,
    ListingStatusError,
    ValidationError,
)
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post(
    "/listings",
    response_model=ListingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new listing",
    description="Create a new listing with draft status",
)
async def create_listing(
    data: CreateListingRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new listing"""
    try:
        service = ListingService(db, current_user["id"])
        listing = await service.create_listing(data, current_user["id"])
        return listing
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message, "field": e.field}
        )
    except Exception as e:
        logger.error(f"Unexpected error creating listing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred"
        )


@router.get(
    "/listings/me",
    response_model=List[ListingResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current user's listings",
    description="Get all listings created by the current user",
)
async def get_my_listings(
    skip: int = Query(0, ge=0, description="Number of listings to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of listings to return"),
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's listings"""
    try:
        service = ListingService(db, current_user["id"])
        listings = await service.get_my_listings(skip, limit)
        return listings
    except Exception as e:
        logger.error(f"Unexpected error getting user's listings: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred"
            }
        )


@router.get(
    "/listings",
    response_model=ListingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Search listings",
    description="Search listings by various criteria",
)
async def search_listings(
    city: Optional[str] = Query(None, description="Filter by city"),
    sub_city: Optional[str] = Query(None, description="Filter by sub-city"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    bedrooms: Optional[int] = Query(None, ge=0, description="Number of bedrooms"),
    bathrooms: Optional[int] = Query(None, ge=0, description="Number of bathrooms"),
    property_type: Optional[str] = Query(None, description="Property type"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db),
):
    """Search listings by various criteria"""
    try:
        service = ListingService(db)
        listings, total = await service.search_listings(
            city,
            sub_city,
            min_price,
            max_price,
            bedrooms,
            bathrooms,
            property_type,
            skip,
            limit,
        )
        return ListingsResponse(
            items=listings,
            total=total,
            page=(skip // limit) + 1,
            limit=limit,
            total_pages=(total + limit - 1) // limit,
        )
    except Exception as e:
        logger.error(f"Unexpected error searching listings: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get(
    "/listings/{listing_id}",
    response_model=ListingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get listing by ID",
    description="Get a specific listing by ID",
)
async def get_listing(
    listing_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific listing by ID"""
    try:
        service = ListingService(db)
        listing = await service.get_listing(listing_id)
        return listing
    except ListingNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": e.code,
                "message": e.message,
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error getting listing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.put(
    "/listings/{listing_id}",
    response_model=ListingResponse,
    status_code=status.HTTP_200_OK,
    summary="Update listing",
    description="Update a specific listing by ID",
)
async def update_listing(
    listing_id: UUID,
    data: UpdateListingRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a specific listing by ID"""
    try:
        service = ListingService(db, current_user["id"])
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "NO_FIELDS_TO_UPDATE", "message": "No fields provided for update"}
            )
        listing = await service.update_listing(listing_id, update_data)
        return listing
    except ListingNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message}
        )
    except ListingPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": e.code, "message": e.message}
        )
    except ListingStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": e.code, "message": e.message}
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": e.code, "message": e.message, "field": e.field}
        )
    except Exception as e:
        logger.error(f"Unexpected error updating listing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred"
        )


@router.delete(
    "/listings/{listing_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete listing",
    description="Delete a specific listing by ID",
)
async def delete_listing(
    listing_id: UUID,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a specific listing by ID"""
    try:
        service = ListingService(db, current_user["id"])
        await service.delete_listing(listing_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ListingNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message}
        )
    except ListingPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": e.code, "message": e.message}
        )
    except ListingStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": e.code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting listing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred"
        )
