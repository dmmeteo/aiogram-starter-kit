from typing import TypeVar, Generic, Type, Optional, Any
from collections.abc import Sequence

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.entities import BaseEntity

TEntity = TypeVar('TEntity', bound=BaseEntity)


class Repository(Generic[TEntity]):
    def __init__(self, session: AsyncSession, entity: Type[TEntity]) -> None:
        self.session = session
        self.entity = entity

    async def get(self, ident: int | str) -> Optional[TEntity]:
        return await self.session.get(entity=self.entity, ident=ident)

    async def get_by_where(self, whereclause: Any) -> Optional[TEntity]:
        statement = select(self.entity).where(whereclause)

        return (await self.session.execute(statement)).one_or_none()

    async def get_many(
        self,
        whereclause: Any,
        offset: int = 0,
        limit: int = 100,
        order_by: Any = None,
    ) -> Sequence[TEntity]:
        statement = select(self.entity).where(whereclause).offset(offset).limit(limit)

        if order_by:
            statement = statement.order_by(order_by)

        return (await self.session.scalars(statement)).all()

    async def add(self, record: TEntity) -> TEntity:
        await self.session.add(record)
        await self.session.flush()

        return record

    async def update(self, record: TEntity) -> TEntity:
        await self.session.merge(record)
        await self.session.flush()

        return record

    async def delete(self, whereclause: Any) -> None:
        statement = delete(self.entity).where(whereclause)
        await self.session.execute(statement)
