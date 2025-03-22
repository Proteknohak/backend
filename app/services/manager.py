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
    
    async def add_user_to_room(self, room_id: str, user_id: str) -> Room:
        return await self.room_service.add_user_to_room(room_id, user_id)

    async def remove_user_from_room(self, room_id: str, user_id: str) -> Room:
        return await self.room_service.remove_user_from_room(room_id, user_id)
    
    async def change_user_lang(self, user_id: str, lang: str) -> User:
        return await self.user_service.change_user_lang(user_id, lang)
    
    async def get_room_info(self, room_id: str) -> Room:
        return await self.room_service.get_room_by_id(room_id)
    
    async def get_all_users(self) -> list[Room]:
        return await self.user_service.get_all_users()