from fastapi import APIRouter, Request, Response
from app.schemas.user import User

from app.schemas.room import Room

router = APIRouter()

@router.post(
    '/room'
)
async def create_room(request: Request) -> User:
    '''
    body:
    id: str,
    creator_id: str
    '''
    user_data = await request.json()
    user: User = User(**user_data, is_creator=False)

    return user


@router.get(
    '/room/{id}'
)
async def join_room(id: str) -> Room:
    '''
    return room_id, creator_id, users
    '''
    pass
