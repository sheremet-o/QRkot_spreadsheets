from http import HTTPStatus

from fastapi import HTTPException
from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charityproject_crud
from app.models import CharityProject

PROJECT_NOT_FOUND = 'Проект не найден.'
PROJECT_EXISTS = 'Проект с таким именем уже существует!'
FORBIDDEN_UPDATE = 'Закрытый проект нельзя редактировать!'
INVESTED_RPOJECT_DELETION = (
    'В проект были внесены средства, не подлежит удалению!'
)
INVALID_INVESTED_AMOUNT = (
    'Нельзя установить требуемую сумму меньше уже '
    'вложенной - {project_invested_amount}.'
)


async def check_charity_project_exists(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    charity_project = await charityproject_crud.get_charity_project(
        object_id=project_id, session=session
    )
    if not charity_project:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=PROJECT_NOT_FOUND
        )
    return charity_project


async def check_name_duplicate(
    project_name: str,
    session: AsyncSession
) -> None:
    charity_project_id = await (
        charityproject_crud.get_charity_project_id_by_name(
            project_name=project_name, session=session
        )
    )
    if charity_project_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=PROJECT_EXISTS
        )


async def check_project_was_closed(
    project_id: int,
    session: AsyncSession
):
    project_close_date = await (
        charityproject_crud.get_charity_project_close_date(
            project_id, session
        )
    )
    if project_close_date:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=FORBIDDEN_UPDATE
        )


async def check_project_was_invested(
    project_id: int,
    session: AsyncSession
):
    invested_project = await (
        charityproject_crud.get_charity_project_invested_amount(
            project_id, session
        )
    )
    if invested_project:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=INVESTED_RPOJECT_DELETION
        )


async def check_correct_full_amount_for_update(
    project_id: int,
    session: AsyncSession,
    full_amount_to_update: PositiveInt
):
    db_project_invested_amount = await (
        charityproject_crud.get_charity_project_invested_amount(
            project_id, session
        )
    )
    if db_project_invested_amount > full_amount_to_update:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=INVALID_INVESTED_AMOUNT.format(db_project_invested_amount)
        )
