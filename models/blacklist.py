from sqlalchemy import Column, Integer, String
from .database import _Base, _db
from bot.app import get_time


class BlacklistModel(_Base):
    __tablename__ = 'blacklist'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    kwork_user_id = Column(String(32), nullable=False)
    creation_time = Column(Integer, nullable=False)


def create(user_id: int, kwork_user_id: str) -> BlacklistModel:
    try:
        Blacklist = BlacklistModel(
            user_id=user_id,
            kwork_user_id=kwork_user_id,
            creation_time=get_time()
        )
        _db.add(Blacklist)
        _db.commit()

        return Blacklist if Blacklist else None

    except Exception as ex:
        print(ex)

    return None


def delete(Blacklist_id) -> BlacklistModel:
    try:
        Blacklist = _db.query(BlacklistModel).get(Blacklist_id)

        _db.delete(Blacklist)
        _db.commit()
        
        return Blacklist if Blacklist else None

    except Exception as ex:
        print(ex)

    return None


def get_by_owner(user_id: int, kwork_user_id: str) -> list:
    try:
        Blacklist = _db.query(BlacklistModel).filter_by(user_id=user_id, kwork_user_id=kwork_user_id).first()
        return Blacklist if Blacklist else None

    except Exception as ex:
        print(ex)

    return None


def get_all_by_owner(user_id: int) -> list:
    try:
        Blacklists = _db.query(BlacklistModel).filter_by(user_id=user_id).all()
        return Blacklists if Blacklists else []

    except Exception as ex:
        print(ex)

    return []
