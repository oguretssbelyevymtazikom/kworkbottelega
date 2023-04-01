from sqlalchemy import Column, Integer, Boolean
from .database import _Base, _db
from bot.app import get_time


class ReferralModel(_Base):
    __tablename__ = 'referrals'

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, nullable=False)
    referral_id = Column(Integer, nullable=False, unique=True)
    activated = Column(Boolean, nullable=False, default=False)
    creation_time = Column(Integer, nullable=False)


def create(referrer_id: int, referral_id: int) -> ReferralModel:
    try:
        Referral = ReferralModel(
            referrer_id=referrer_id,
            referral_id=referral_id,
            creation_time=get_time()
        )

        _db.add(Referral)
        _db.commit()

        return Referral if Referral else None

    except Exception as ex:
        print(ex)

    return None


def activate(referral_id: int):
    try:
        Referral = _db.query(ReferralModel).filter_by(referral_id=referral_id).first()

        Referral.activated = True
        _db.add(Referral)
        _db.commit()

        return Referral if Referral else None
    
    except Exception as ex:
        print(ex)

    return None


def delete(referral_id: int):
    try:
        Referral = _db.query(ReferralModel).filter_by(referral_id=referral_id).first()

        _db.delete(Referral)
        _db.commit()

        return Referral if Referral else None
    
    except Exception as ex:
        print(ex)

    return None


def get(referral_id: int):
    try:
        Referral = _db.query(ReferralModel).filter_by(referral_id=referral_id).first()
        return Referral if Referral else None
    
    except Exception as ex:
        print(ex)

    return None


def get_all() -> ReferralModel:
    try:
        Referrals = _db.query(ReferralModel).all()
        return Referrals if Referrals else []

    except Exception as ex:
        print(ex)

    return []


def get_all_active() -> ReferralModel:
    try:
        Referrals = _db.query(ReferralModel).filter_by(activated=True).all()
        return Referrals if Referrals else []

    except Exception as ex:
        print(ex)

    return []


def get_all_by_owner(referrer_id: int) -> ReferralModel:
    try:
        Referrals = _db.query(ReferralModel).filter_by(referrer_id=referrer_id).all()
        return Referrals if Referrals else []

    except Exception as ex:
        print(ex)

    return []


def get_all_active_by_owner(referrer_id: int) -> ReferralModel:
    try:
        Referrals = _db.query(ReferralModel).filter_by(referrer_id=referrer_id, activated=True).all()
        return Referrals if Referrals else []

    except Exception as ex:
        print(ex)

    return []
