from sqlalchemy import Column, Integer, String, Boolean
from .database import _Base, _db
from bot.app import get_time


class PaymentModel(_Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, nullable=False)
    payment_id = Column(String(64), nullable=False)
    amount = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    status = Column(Boolean, nullable=False, default=False)
    creation_time = Column(Integer, nullable=False, default=get_time())


def create(client_id: int, payment_id: str, amount: int, price: int) -> PaymentModel:
    try:
        Payment = PaymentModel(
            client_id=client_id,
            payment_id=payment_id,
            amount=amount,
            price=price
        )
        _db.add(Payment)
        _db.commit()

        return Payment if Payment else None

    except Exception as ex:
        print(ex)

    return None


def get(payment_id: str) -> PaymentModel:
    try:
        Payment = _db.query(PaymentModel).filter_by(payment_id=payment_id).first()
        return Payment if Payment else []

    except Exception as ex:
        print(ex)

    return []


def get_all() -> list:
    try:
        Payments = _db.query(PaymentModel).all()
        return Payments if Payments else []

    except Exception as ex:
        print(ex)

    return []


def get_all_by_client(client_id: int) -> list:
    try:
        Payments = _db.query(PaymentModel).filter_by(client_id=client_id).all()
        return Payments if Payments else []

    except Exception as ex:
        print(ex)

    return []


def get_all_active_by_client(client_id: int) -> list:
    try:
        Payments = _db.query(PaymentModel).filter_by(client_id=client_id, status=True).all()
        return Payments if Payments else []

    except Exception as ex:
        print(ex)

    return []


def get_all_unactive_by_client(client_id: int) -> list:
    try:
        Payments = _db.query(PaymentModel).filter_by(client_id=client_id, status=False).all()
        return Payments if Payments else []

    except Exception as ex:
        print(ex)

    return []


def complete(payment_id: str) -> PaymentModel:
    try:
        Payment = _db.query(PaymentModel).filter_by(payment_id=payment_id).first()

        Payment.status = True
        _db.add(Payment)
        _db.commit()

        return Payment if Payment else None

    except Exception as ex:
        print(ex)

    return None


def delete(payment_id: str) -> PaymentModel:
    try:
        Payment = _db.query(PaymentModel).filter_by(payment_id=payment_id).first()

        _db.delete(Payment)
        _db.commit()

        return Payment if Payment else None

    except Exception as ex:
        print(ex)

    return None
