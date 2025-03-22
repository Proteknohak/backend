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
    name: str
    lang: str
    '''
    data: dict = await request.json()
    user: User = await manager.add_user(AddUser(**data))
    return user

@router.patch(
    '/user/{user_id}'
)
async def change_lang(user_id: str, request: Request, manager: Manager = Depends()) -> User:
    data: dict = await request.json()
    lang: str = data.get('lang')
    user: User = await manager.change_user_lang(user_id, lang)
    return user

@router.get(
    '/user'
)
async def get_all_users(manager: Manager = Depends()) -> list[User]:
    return await manager.get_all_users()