from fastapi import APIRouter, Depends, status
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get(
    "/me",
    response_model=dict,
    summary="Get current user profile",
    description="Returns the profile of the authenticated user.",
)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Returns the current authenticated user"""
    return current_user