from pydantic import BaseModel, ConfigDict

class Room(BaseModel):
    id: str
    creator_id: str
    users: list[str]

    model_config = ConfigDict(from_attributes=True)

class AddRoom(BaseModel):
    creator_id: str

    model_config = ConfigDict(from_attributes=True)