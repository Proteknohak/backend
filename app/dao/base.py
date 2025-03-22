from typing import Any
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, create_model

from db.database import Base

class BaseDAO[T: Base]:
    model: T

    def __init_subclass__(cls):
        cls.model = cls.__orig_bases__[0].__args__[0]

    @classmethod
    async def add(cls, session: AsyncSession, instance: BaseModel) -> T:
        new_instance: T = cls.model(**instance.model_dump(exclude_unset=True))
        session.add(new_instance)
        try:
            await session.flush()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        return new_instance
    
    @classmethod
    async def add_many(cls, session: AsyncSession, instances: list[BaseModel]) -> list[T]:
        new_instances: list[T] = [cls.model(**instance.model_dump(exclude_unset=True)) for instance in instances]
        session.add_all(new_instances)
        try:
            await session.flush()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        return new_instances
    
    @classmethod
    async def find_one_or_none_by_id(cls, session: AsyncSession, data_id: int) -> T | None:
        IdModel = create_model("IdModel", data_id=(int, ...))
        try:
            return await session.get(cls.model, IdModel(data_id=data_id).data_id)
        except SQLAlchemyError as e:
            raise

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, filters: BaseModel) -> T | None:
        filter_dict = filters.model_dump(exclude_unset=True)
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            record: T | None = result.scalar_one_or_none()
            return record
        except SQLAlchemyError as e:
            raise
    
    @classmethod
    async def find_all(cls, session: AsyncSession, filters: BaseModel | None) -> list[T] | None:
        if filters:
            filter_dict: dict = filters.model_dump(exclude_unset=True)
        else:
            filter_dict: dict = {}
        try:
            query = select(cls.model).filter_by(filter_dict)
            result = await session.execute(query)
            records: list[T] = result.scalars().all()
            return records
        except SQLAlchemyError as e:
            raise
    
    @classmethod
    async def update_one_by_id(cls, session: AsyncSession, data_id: int, instance: BaseModel) -> int:
        try:
            record: T | None = await session.get(cls.model, data_id)
            if record is None:
                return 0
            for key, value in instance.model_dump().items():
                setattr(record, key, value)
            await session.flush()
            return 1
        except SQLAlchemyError as e:
            raise 

    @classmethod
    async def update_many(cls, session: AsyncSession, filter_criteria: BaseModel, values: BaseModel) -> int:
        try:
            stmt = (
                update(cls.model)
                .filter_by(**filter_criteria.model_dump())
                .values(**values.model_dump())
            )
            result = await session.execute(stmt)
            await session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            raise

    @classmethod
    async def delete_one_by_id(cls, sesion: AsyncSession, data_id: int) -> int:
        try:
            data: T | None = await sesion.get(cls.model, data_id)
            if data:
                await sesion.delete(data)
                await sesion.flush()
                return 1
            return 0
        except SQLAlchemyError as e:
            raise

    @classmethod
    async def delete_many(cls, session: AsyncSession, filters: BaseModel | None, *args, force_delete=False) -> int:
        if force_delete:
            stmt = delete(cls.model)
        else:
            if filters is None:
                raise Exception().add_note("Are you sure want to delete all records? If yes, use force_delete=True")
            stmt = delete(cls.model).filter_by(**filters.model_dump())
        try:
            result = await session.execute(stmt)
            await session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            raise
