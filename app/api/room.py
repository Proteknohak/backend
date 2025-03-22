from fastapi import APIRouter, Request, Response, Depends
from app.schemas.user import User
from app.schemas.room import Room, AddRoom

from app.services.manager import Manager

router = APIRouter()

@router.post(
    '/room'
)
async def create_room(request: Request, manager: Manager = Depends()) -> Room:
    '''
    body:
    id: str,
    creator_id: str
    '''
    data = await request.json()
    room: Room = await manager.add_room(AddRoom(**data))
    return room


@router.get(
    '/room/{room_id}'
)
async def join_room(room_id: str, user_id: str | None = None, manager: Manager = Depends()) -> Room:
    if user_id is None:
        return await manager.get_room_info(room_id)
    return await manager.add_user_to_room(room_id, user_id)

@router.delete(
    '/room/{room_id}'
)
async def leave_room(room_id: str, user_id: str, manager: Manager = Depends()) -> Room:
    return await manager.remove_user_from_room(room_id, user_id)