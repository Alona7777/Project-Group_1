from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.services.roles import RoleAccess
from src.database.db import get_db
from src.entity.models import User, Role
from src.schemas.rating import RatingModel, RatingResponse
from src.repository import rating as repository_ratings
# from src.conf.messages import me

from src.services.auth import auth_service

router = APIRouter(prefix='/ratings', tags=["ratings"])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get("/image/{image_id}", response_model=int, dependencies=[Depends(access_to_route_all)])
async def get_common_rating(image_id: int, db: AsyncSession = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)):
    average_rating = await repository_ratings.get_average_rating(image_id, db)
    return average_rating


@router.get("/{rating_id}", response_model=RatingResponse, dependencies=[Depends(access_to_route_all)])
async def read_rating(rating_id: int, db: AsyncSession = Depends(get_db)):
    rating = await repository_ratings.get_rating(rating_id, db)
    if rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    return rating


@router.post("/{image_id}", response_model=RatingResponse, dependencies=[Depends(access_to_route_all)])
async def create_rating(image_id: int, body: RatingModel, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    rating = await repository_ratings.create_rating_from_user(image_id, body, current_user, db)
    if rating is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot rate the image (e.g., own image or duplicated rating)")
    return rating


@router.put("/{rating_id}", response_model=RatingResponse, dependencies=[Depends(access_to_route_all)])
async def update_rating(rating_id: int, body: RatingModel, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    rating = await repository_ratings.update_rating(rating_id, body, db)
    if rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Rating not found or unauthorized update attempt")
    return rating


@router.delete("/{rating_id}", response_model=RatingResponse, dependencies=[Depends(access_to_route_all)])
async def remove_rating(rating_id: int, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    rating = await repository_ratings.remove_rating(rating_id, db)
    if rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Rating not found or unauthorized deletion attempt")
    return rating
