from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.dao import RoomDAO
from app.dao.session_maker import connection
from app.schemas.room import Room as RoomSchema, AddRoom as AddRoomSchema
from app.schemas.user import User as UserSchema
from db.models import User, Room

class RoomService:
    def __init__(self):
        self.roomdao = RoomDAO()

    @connection()
    async def add_room(self, room_data: AddRoomSchema, *args, session: AsyncSession) -> RoomSchema:
        room: Room = await self.roomdao.add_room(session, room_data)
        return RoomSchema(**room.__dict__)

    @connection(commit=False)
    async def get_room_by_id(self, room_id: str, *args, session: AsyncSession) -> RoomSchema:
        room: Room = await self.roomdao.get_room_by_id(session, room_id)
        return RoomSchema(**room.__dict__)
    
    @connection(commit=False)
    async def get_room_users(self, room_id: str, *args, session: AsyncSession) -> list[str]:
        users: list[str] = await self.roomdao.get_room_users(session, room_id)
        return users
    
    @connection()
    async def add_user_to_room(self, room_id: str, user_id: str, *args, session: AsyncSession) -> RoomSchema:
        room: Room = await self.roomdao.add_user_to_room(session, user_id, room_id)
        return RoomSchema(**room.__dict__)

    @connection()
    async def remove_user_from_room(self, room_id: str, user_id: str, *args, session: AsyncSession) -> RoomSchema:
        room: Room = await self.roomdao.remove_user_from_room(session, user_id, room_id)
        return RoomSchema(**room.__dict__)