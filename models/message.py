from sqlalchemy import Column, Integer
from .database import _Base, _db
from bot.app import get_time


class MessageModel(_Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    message_id = Column(Integer, nullable=False)
    creation_time = Column(Integer, nullable=False)


def create(user_id: int, message_id: int) -> MessageModel:
    try:
        Message = MessageModel(
            user_id=user_id,
            message_id=message_id,
            creation_time=get_time()
        )
        _db.add(Message)
        _db.commit()

        return Message if Message else None

    except Exception as ex:
        print(ex)

    return None


def get(user_id: int, message_id: int) -> MessageModel:
    try:
        Message = _db.query(MessageModel).filter_by(user_id=user_id, message_id=message_id).first()
        return Message if Message else None

    except Exception as ex:
        print(ex)

    return None


def get_all() -> list:
    try:
        Messages = _db.query(MessageModel).all()
        return Messages if Messages else []

    except Exception as ex:
        print(ex)

    return []


def get_all_by_user(user_id: int) -> list:
    try:
        Messages = _db.query(MessageModel).filter_by(user_id=user_id).all()
        return Messages if Messages else []

    except Exception as ex:
        print(ex)

    return []


def delete(user_id: int, message_id: int) -> MessageModel:
    try:
        Message = _db.query(MessageModel).filter_by(user_id=user_id, message_id=message_id).first()
        
        _db.delete(Message)
        _db.commit()

        return Message if Message else None

    except Exception as ex:
        print(ex)

    return None
