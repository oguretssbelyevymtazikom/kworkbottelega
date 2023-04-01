from sqlalchemy import Column, Integer, String, Boolean
from .database import _Base, _db
from bot.app import get_time


class LinkModel(_Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, nullable=False)
    name = Column(String(32), nullable=False)
    url = Column(String(500), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    creation_time = Column(Integer, nullable=False)


def create(owner_id: int, name: str, url: str) -> LinkModel:
    try:
        Link = LinkModel(
            owner_id=owner_id,
            name=name,
            url=url,
            creation_time=get_time()
        )
        _db.add(Link)
        _db.commit()

        return Link if Link else None

    except Exception as ex:
        print(ex)

    return None


def get(link_id: int) -> LinkModel:
    try:
        Link = _db.query(LinkModel).get(link_id)
        return Link if Link else None

    except Exception as ex:
        print(ex)

    return None


def get_all() -> list:
    try:
        Links = _db.query(LinkModel).all()
        return Links if Links else []

    except Exception as ex:
        print(ex)

    return []


def get_all_active() -> list:
    try:
        Links = _db.query(LinkModel).filter_by(active=True).all()
        return Links if Links else []

    except Exception as ex:
        print(ex)

    return []


def get_all_active_by_owner(owner_id: int) -> list:
    try:
        Links = _db.query(LinkModel).filter_by(owner_id=owner_id, active=True).all()
        return Links if Links else []

    except Exception as ex:
        print(ex)

    return []


def get_by_owner_url(owner_id: int, link_url: str) -> LinkModel:
    try:
        Link = _db.query(LinkModel).filter_by(owner_id=owner_id, url=link_url).first()
        return Link if Link else None

    except Exception as ex:
        print(ex)

    return None


def get_by_owner_name(owner_id: int, name: str) -> list:
    try:
        Link = _db.query(LinkModel).filter_by(owner_id=owner_id, name=name).first()
        return Link if Link else None

    except Exception as ex:
        print(ex)

    return None


def get_all_by_owner(owner_id: int) -> list:
    try:
        Links = _db.query(LinkModel).filter_by(owner_id=owner_id).all()
        return Links if Links else []

    except Exception as ex:
        print(ex)

    return []


def toggle(link_id: int):
    try:
        Link = get(link_id)
        
        Link.active = not Link.active
        _db.add(Link)
        _db.commit()

        return Link if Link else None

    except Exception as ex:
        print(ex)

    return None


def delete(link_id: int):
    try:
        Link = get(link_id)

        _db.delete(Link)
        _db.commit()

        return True

    except Exception as ex:
        print(ex)

    return False
