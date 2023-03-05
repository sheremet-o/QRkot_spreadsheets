from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import DonationCreate, DonationDB
from app.services.investment import execute_investment_process

EXCLUDE_FIELDS = (
    'user_id',
    'invested_amount',
    'fully_invested',
    'close_date'
)

router = APIRouter()


@router.get(
    '/',
    response_model=List[DonationDB],
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True
)
async def get_all_donations_superuser(
    session: AsyncSession = Depends(get_async_session),
):

    donations = await donation_crud.get_multiple(session)
    return donations


@router.get(
    '/my',
    response_model=List[DonationDB],
    response_model_exclude={*EXCLUDE_FIELDS}
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    donations = await donation_crud.get_donations_by_user(
        session=session, user=user
    )
    return donations


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude={*EXCLUDE_FIELDS},
    response_model_exclude_none=True
)
async def create_new_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):

    new_donation = await donation_crud.create(
        donation, session, user
    )
    await execute_investment_process(new_donation, session)
    await session.refresh(new_donation)
    return new_donation
