from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    id: str
    name: str
    lang: str
    is_creator: bool

    model_config = ConfigDict(from_attributes=True)

class AddUser(BaseModel):
    name: str
    lang: str

    model_config = ConfigDict(from_attributes=True)
