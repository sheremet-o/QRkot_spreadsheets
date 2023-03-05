from typing import Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base
from app.models import User

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=Optional[BaseModel])


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(
        self,
        model: Type[ModelType]
    ):
        self.model = model

    async def get_multiple(
        self,
        session: AsyncSession
    ) -> List[ModelType]:
        db_objects = await session.execute(select(self.model))
        return db_objects.scalars().all()

    async def create(
        self,
        object_in,
        session: AsyncSession,
        user: Optional[User] = None
    ) -> ModelType:
        object_in_data = object_in.dict()

        if user is not None:
            object_in_data['user_id'] = user.id

        db_object = self.model(**object_in_data)

        session.add(db_object)
        await session.commit()
        await session.refresh(db_object)
        return db_object
