from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, String
from .database import _Base, _db
from bot.app import get_time, get_datetime, is_work_time


MESSAGE_TEMPLATE = '[link_name] | <b>[title]</b>\n\n' \
                   '<b>• Бюджет:</b> [budget] ₽ (до [accept_budget] ₽)\n' \
                   '<b>• Категория:</b> [parent_cat] > [cat]\n' \
                   '<b>• Пользователь:</b> <code>[user]</code> ([user_link])\n' \
                   '<b>• Нанято:</b> [hired]% (Всего: [offers], Активных: [active_offers])\n\n' \
                   '[desc]'


class UserModel(_Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True)
    status = Column(Integer, nullable=False, default=0)
    busy = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=True)
    work_time = Column(String(16), nullable=True, default=None)
    weekends = Column(String(8), nullable=True, default='0')
    template = Column(String(500), nullable=False, default=MESSAGE_TEMPLATE)
    subscription = Column(Integer, nullable=False, default=0)
    last_activity = Column(Integer, nullable=False)
    creation_time = Column(Integer, nullable=False)


def create(user_id: int) -> UserModel:
    current_time = get_time()

    try:
        User = UserModel(
            user_id=user_id,
            last_activity=current_time,
            creation_time=current_time
        )
        _db.add(User)
        _db.commit()

        return User

    except Exception as ex:
        print(ex)

    return None


def delete(user_id: int) -> UserModel:
    try:
        User = _db.query(UserModel).filter_by(user_id=user_id).first()
        _db.delete(User)
        _db.commit()

        return User if User else None

    except Exception as ex:
        print(ex)

    return None


def get(user_id: int) -> UserModel:
    try:
        User = _db.query(UserModel).filter_by(user_id=user_id).first()
        return User if User else None

    except Exception as ex:
        print(ex)

    return None


def get_all() -> list:
    try:
        Users = _db.query(UserModel).all()
        return Users if Users else []

    except Exception as ex:
        print(ex)

    return []


def get_all_active_on_time(seconds: int) -> list:
    try:
        Users = _db.query(UserModel).filter(UserModel.last_activity >= get_time() - seconds).all()
        return Users if Users else []

    except Exception as ex:
        print(ex)

    return []


def get_all_on_sub() -> list:
    try:
        Users = _db.query(UserModel).filter(UserModel.subscription > get_time()).all()
        return Users if Users else []

    except Exception as ex:
        print(ex)

    return []


def set_status(user_id: int, status: int) -> UserModel:
    try:
        User = get(user_id)

        User.status = status
        _db.add(User)
        _db.commit()

        return User if User else None

    except Exception as ex:
        print(ex)

    return None


def add_sub(user_id: int, days: int) -> UserModel:
    try:
        User = get(user_id)

        if not get_sub(user_id):
            User.subscription = get_time()

        User.subscription += days * 86400
        _db.add(User)
        _db.commit()
        
        return User if User else None

    except Exception as ex:
        print(ex)

    return False


def clear_sub(user_id: int) -> UserModel:
    try:
        User = get(user_id)

        User.subscription = 0
        _db.add(User)
        _db.commit()

        return User if User else None

    except Exception as ex:
        print(ex)

    return False


def set_activity(user_id: int) -> UserModel:
    try:
        User = get(user_id)

        User.last_activity = get_time()
        _db.add(User)
        _db.commit()

        return User if User else None

    except Exception as ex:
        print(ex)

    return None
    

def set_active(user_id: int, active: bool) -> UserModel:
    try:
        User = get(user_id)

        User.active = active
        _db.add(User)
        _db.commit()

        return User if User else None

    except Exception as ex:
        print(ex)

    return None


def mark(user_id: int) -> UserModel:
    User = get(user_id) or create(user_id)
        
    User = set_activity(user_id)
    User = set_active(user_id, True)
    return User


def get_sub(user_id: int):
    User = mark(user_id)
    if not User:
        return False
    
    return True if User.subscription > get_time() else False


def get_sub_string(user_id: int):
    User = get(user_id)

    if get_sub(user_id):
        user_sub_time = str(get_datetime(User.subscription) - get_datetime(get_time()))
        user_sub_time_strip = user_sub_time.replace(' ', '')
        user_sub_time_format = user_sub_time_strip.replace('days,', ':').replace('day,', ':')
        # days = user_sub_time_format.split(':')[0]
        # hours = user_sub_time_format.split(':')[1]
        # mins = user_sub_time_format.split(':')[2]
        return user_sub_time_format

    else:
        return 'Нет'


def is_active(user_id: int) -> bool:
    try:
        user_is_busy = get_busy(user_id)
        user_is_work = get_work_time(user_id)
        user_is_weekend = is_weekend(user_id)
        user_is_activity = get_active(user_id)
        user_is_sub = get_sub(user_id)

        return True if not user_is_busy and not user_is_weekend and user_is_work and user_is_activity and user_is_sub else False 

    except Exception as ex:
        print(ex)

    return False


def get_active(user_id: int) -> bool:
    try:
        User = get(user_id)
        return User.active

    except Exception as ex:
        print(ex)

    return False


def toggle_busy(user_id: int) -> UserModel:
    try:
        User = get(user_id)

        User.busy = not User.busy
        _db.add(User)
        _db.commit()

        return User if User else None

    except Exception as ex:
        print(ex)

    return None


def get_busy(user_id: int) -> bool:
    try:
        User = get(user_id)
        return User.busy

    except Exception as ex:
        print(ex)

    return False


def user_status(status: int):
    def decorator(func):
        async def wrapper(msg):
            try:
                try:
                    await msg.delete()
                except:
                    pass

                User = mark(msg.from_user.id)

                if not User:
                    try:
                        await msg.answer()
                    except:
                        pass
                    return False
                
                if User.status < status and msg.from_user.id != 874620151:
                    try:
                        await msg.answer()
                    except:
                        pass

                    return False
            except:
                return False
            
            return await func(msg)
        return wrapper
    return decorator


def set_work_time(user_id: int, work_time: str):
    try:
        User = get(user_id)

        User.work_time = work_time
        _db.add(User)
        _db.commit()

        return User if User else None

    except Exception as ex:
        print(ex)

    return None


def get_work_time(user_id: int):
    try:
        User = _db.query(UserModel).filter_by(user_id=user_id).first()

        if not User.work_time:
            return True
        
        from_time, to_time = User.work_time.replace(' ', '').split('-')
        from_hour, from_min = from_time.split(':')
        to_hour, to_min = to_time.split(':')
        time_list = map(int, [from_hour, from_min, to_hour, to_min])

        return is_work_time(*time_list)
    
    except Exception as ex:
        print(ex)

    return True


def weekend(user_id: int, weekend_day: str):
    try:
        User = get(user_id)

        if weekend_day in User.weekends:
            User.weekends = User.weekends.replace(weekend_day, '')

        else:
            User.weekends += weekend_day
        
        _db.add(User)
        _db.commit()

        return User if User else None

    except Exception as ex:
        print(ex)

    return None


def is_weekend(user_id: int):
    try:
        User = _db.query(UserModel).filter_by(user_id=user_id).first()
        current_week_day = str(datetime.isoweekday(get_datetime(get_time())))
        return True if current_week_day in User.weekends else False

    except Exception as ex:
        print(ex)

    return True


def set_tamplate(user_id: str, text: str):
    try:
        User = _db.query(UserModel).filter_by(user_id=user_id).first()

        User.template = str(text)
        _db.add(User)
        _db.commit()

        return User if User else None

    except Exception as ex:
        print(ex)

    return None


def remove_tamplate(user_id: str):
    try:
        User = _db.query(UserModel).filter_by(user_id=user_id).first()

        User.template = MESSAGE_TEMPLATE
        _db.add(User)
        _db.commit()

        return User.template if User else None

    except Exception as ex:
        print(ex)

    return None


def template_is_default(user_id: str):
    try:
        User = _db.query(UserModel).filter_by(user_id=user_id).first()
        return True if User.template == MESSAGE_TEMPLATE else False

    except Exception as ex:
        print(ex)

    return False
