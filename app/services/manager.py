from app.services.room import RoomService
from app.services.user import UserService

from app.schemas.room import Room, AddRoom
from app.schemas.user import User, AddUser

class Manager:
    def __init__(self):
        self.room_service = RoomService()
        self.user_service = UserService()

    async def add_user(self, user_data: AddUser) -> User:
        return await self.user_service.add_user(user_data)
    
    async def add_room(self, room_data: AddRoom) -> Room:
        return await self.room_service.add_room(room_data)

    