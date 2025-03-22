from fastapi import APIRouter, Request, Response, Depends
from app.schemas.user import User, AddUser
from app.schemas.room import Room, AddRoom
from app.services.manager import Manager

router = APIRouter()

@router.post(
    '/user'
)
async def create_user(request: Request, manager: Manager = Depends()) -> User:
    '''
    body:
    room_id: str
    name: str
    lang: str
    is_creator: bool
    '''
    data: dict = await request.json()
    room_id = data.get('room_id')
    name = data.get('name')
    lang = data.get('lang')
    is_creator = bool(data.get('is_creator'))
    user: User = await manager.add_user(AddUser(
        name=name,
        lang=lang,
    ))
    if is_creator:
        await manager.add_room(AddRoom(
            creator_id=user.id
        ))
    return user
