from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, func
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


    classmethod
    async def get_user_by_id(cls, session: AsyncSession, user_id: str) -> User | None:
        return await cls.find_one_or_none(session, create_model(
            'UserIdModel', user_id=(str, ...)
        )(user_id=user_id))
    

class RoomDAO(BaseDAO[Room]):
    @classmethod
    async def add_room(cls, session: AsyncSession, room_data: AddRoomSchema) -> Room:
        room_dict: dict = room_data.model_dump()
        room_dict['id'] = str(uuid4())
        room_dict['users'] = []
        room: Room = cls.model(**room_dict)
        session.add(room)
        try:
            await session.flush()
            return room
        except SQLAlchemyError:
            await session.rollback()
            raise

    async def get_room_by_id(cls, session: AsyncSession, room_id: str) -> Room:
        return await cls.find_one_or_none(session, create_model(
            'RoomIdModel', room_id=(str, ...)
        )(room_id=room_id))

    async def get_room_users(cls, session: AsyncSession, room_id: str) -> list[str]:
        return await cls.find_one_or_none(session, create_model(
            'RoomIdModel', room_id=(str, ...)
        )(room_id=room_id)).users
    
    async def add_user_to_room(cls, session: AsyncSession, user_id: str, room_id: str) -> Room:
        try:
            room: Room = await session.get(Room, room_id)
            if room is None:
                raise SQLAlchemyError
            room.users.append(user_id)
            await session.flush()
            return room
        except SQLAlchemyError:
            raise
