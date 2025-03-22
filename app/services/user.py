from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.dao import UserDAO
from app.dao.session_maker import connection
from app.schemas.room import Room as RoomSchema
from app.schemas.user import User as UserSchema, AddUser as AddUserSchema
from db.models import User, Room

class UserService:
    def __init__(self):
        self.userdao = UserDAO()

    @connection()
    async def add_user(self, user_data: AddUserSchema, *args, session: AsyncSession) -> UserSchema:
        user: User = await self.userdao.add_user(session, user_data)
        return UserSchema(**user.__dict__, is_creator=False)

    @connection(commit=False)
    async def get_user_by_id(self, user_id: str, *args, session: AsyncSession) -> UserSchema:
        user: User = await self.userdao.get_user_by_id(session, user_id)
        return UserSchema(user, is_creator=False)
