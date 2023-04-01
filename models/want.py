from sqlalchemy import Column, Integer, String, Boolean
from .database import _Base, _db
from bot.app import get_time


class WantModel(_Base):
    __tablename__ = 'wants'

    id = Column(Integer, primary_key=True, index=True)
    want_id = Column(Integer, nullable=False)
    url = Column(String(500), nullable=True)
    sended = Column(Boolean, nullable=False, default=False)
    creation_time = Column(Integer, nullable=False)


def create(want_id: int, url: str) -> WantModel:
    try:
        Want = WantModel(
            want_id=want_id,
            url=url,
            creation_time=get_time()
        )
        _db.add(Want)
        _db.commit()

        return Want if Want else None

    except Exception as ex:
        print(ex)

    return None


def get(want_id: int) -> WantModel:
    try:
        Want = _db.query(WantModel).filter_by(want_id=want_id).first()
        return Want if Want else None

    except Exception as ex:
        print(ex)

    return None


def get_all() -> list:
    try:
        Wants = _db.query(WantModel).all()
        return Wants if Wants else []

    except Exception as ex:
        print(ex)

    return []


def send(want_id: int) -> WantModel:
    try:
        Want = _db.query(WantModel).filter_by(want_id=want_id).first()
        
        Want.sended = True
        _db.add(Want)
        _db.commit()

        return Want if Want else None

    except Exception as ex:
        print(ex)

    return None


def delete_old():
    deleted = 0
    try:
        Wants = _db.query(WantModel).filter(WantModel.sended == False).all()
        
        for Want in Wants:
            _db.delete(Want)
            deleted += 1

        _db.commit()
        
    except Exception as ex:
        print(ex)

    return deleted
