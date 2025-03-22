from datetime import datetime

from sqlalchemy import BigInteger, DateTime, func, ForeignKey, ARRAY, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, class_mapper

from db.database import Base


class User(Base):  # обязательно наследуем все модели от нашей Base-метатаблицы
    __tablename__ = "users"  # Указываем как будет называться наша таблица в базе данных (пишется в ед. числе)

    id: Mapped[str] = mapped_column(String, primary_key=True, index=False)
    name: Mapped[str]
    lang: Mapped[str]

class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    creator_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    users: Mapped[list[str]] = mapped_column(ARRAY(String))