from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, func, update
from pydantic import create_model, constr
from uuid import uuid4

from app.dao.base import BaseDAO
from db.models import User, Room
from app.schemas.user import User as UserSchema, AddUser as AddUserSchema
from app.schemas.room import Room as RoomSchema, AddRoom as AddRoomSchema

class UserDAO(BaseDAO[User]):
    @classmethod
    async def add_user(cls, session: AsyncSession, user_data: AddUserSchema) -> User:
        user_dict: dict = user_data.model_dump()
        user_dict['id'] = str(uuid4())
        user: User = cls.model(**user_dict)
        session.add(user)
        try:
            await session.flush()
            return user
        except SQLAlchemyError:
            await session.rollback()
            raise

    @classmethod
    async def get_user_by_id(cls, session: AsyncSession, user_id: str) -> User | None:
        return await cls.find_one_or_none(session, create_model(
            'UserIdModel', user_id=(str, ...)
        )(id=user_id))
    
    @classmethod
    async def change_user_lang(cls, session: AsyncSession, user_id: str, lang: str) -> User:
        try:
            user: User = await session.get(User, user_id)
            if user is None:
                raise SQLAlchemyError
            user.lang = lang
            await session.flush()
            return user
        except SQLAlchemyError as e:
            raise

    @classmethod
    async def get_all_users(cls, session: AsyncSession) -> list[User]:
        try:
            return (await session.execute(select(User))).scalars().all()
        except SQLAlchemyError as e:
            raise
    

    

class RoomDAO(BaseDAO[Room]):
    @classmethod
    async def add_room(cls, session: AsyncSession, room_data: AddRoomSchema) -> Room:
        room_dict: dict = room_data.model_dump()
        room_dict['users'] = []
        room: Room = cls.model(**room_dict)
        session.add(room)
        try:
            await session.flush()
            return room
        except SQLAlchemyError:
            await session.rollback()
            raise

    @classmethod
    async def get_room_by_id(cls, session: AsyncSession, room_id: str) -> Room:
        return await cls.find_one_or_none(session, create_model(
            'RoomIdModel', id=(str, ...)
        )(id=room_id))

    @classmethod
    async def get_room_users(cls, session: AsyncSession, room_id: str) -> list[str]:
        return await cls.find_one_or_none(session, create_model(
            'RoomIdModel', room_id=(str, ...)
        )(room_id=room_id)).users
    
    @classmethod
    async def add_user_to_room(cls, session: AsyncSession, user_id: str, room_id: str) -> Room:
        try:
            room: Room = await session.get(Room, room_id)
            if room is None:
                raise SQLAlchemyError
            ls: list = getattr(room, 'users', [])
            if user_id not in ls:
                ls2 = ls + [user_id]
                room.users = ls2
                session.add(room)
            await session.flush()
            return room
        except SQLAlchemyError as e:
            raise

    @classmethod
    async def remove_user_from_room(cls, session: AsyncSession, user_id: str, room_id: str) -> Room:
        try:
            room: Room = await session.get(Room, room_id)
            if room is None:
                raise SQLAlchemyError
            ls: list = getattr(room, 'users', [])
            if user_id in ls:
                ls2 = ls[::]
                ls2.remove(user_id)
                room.users = ls2
                session.add(room)
            await session.flush()
            return room
        except SQLAlchemyError as e:
            raise