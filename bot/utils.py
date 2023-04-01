import uuid
from yookassa import Payment
from yookassa.payment import PaymentResponse
from aiogram.types import Message
from bot.app import (
    PAYMAN_FULLNAME,
    PAYMAN_INN,
    PAYMAN_EMAIL,
    PAYMAN_PHONE,
    BOT_USERNAME,
    SUB_DAY_PRICE,
    SUB_REFERRAL_DISCOUNT,
    SUB_YEAR_DISCOUNT,
    bot
)
from models import message, user, referral, link


def subtract_percent(price: int, percent: int):
    return int(price * (1 - (percent / 100)))


def get_sub_price(user_id: int, days: int):
    Referral = referral.get(user_id)
    price = days * SUB_DAY_PRICE

    if days >= 365:
        return subtract_percent(price, SUB_YEAR_DISCOUNT)

    if Referral:
        return subtract_percent(price, SUB_REFERRAL_DISCOUNT)

    return price


async def send_message(*args, **kwargs) -> Message:
    _message = await bot.send_message(*args, **kwargs)
    message.create(_message.chat.id, _message.message_id)
    return _message


def create_payment(user_id: int, price: int, desc: str) -> PaymentResponse:
    return Payment.create({
        'amount': {
            'value': f'{price}.00',
            'currency': 'RUB'
        },
        'confirmation': {
            'type': 'redirect',
            'return_url': f'https://t.me/{BOT_USERNAME}'
        },
        'capture': True,
        'description': desc,  # Не более 128 символов.
        'merchant_customer_id': str(user_id),
        'receipt': {
            'customer': {
                'full_name': PAYMAN_FULLNAME,
                'inn': PAYMAN_INN,
                'email': PAYMAN_EMAIL,
                'phone': PAYMAN_PHONE
            },
            'items': [
                {
                    'description': desc,
                    'amount': {
                        'value': f'{price}.00',
                        'currency': 'RUB'
                    },
                    'vat_code': 1,
                    'quantity': 1
                }
            ]
        }
    }, uuid.uuid4())


def compose_menu_text(user_id: int):
    Referrals = referral.get_all_by_owner(user_id)
    ActiveReferrals = referral.get_all_active_by_owner(user_id)
    ActiveUserLinks = link.get_all_active_by_owner(user_id)

    message = f'Аккаунт: <code><b>{user_id}</b></code>\n' \
              f'Подписка: <b>{user.get_sub_string(user_id)}</b>'

    if Referrals:
        message += f'\nВаши рефералы: <b>{len(ActiveReferrals)} / {len(Referrals)}</b>'

    user_is_sub = user.get_sub(user_id)
    user_is_work = user.get_work_time(user_id)
    user_is_busy = user.get_busy(user_id)
    user_is_weekend = user.is_weekend(user_id)

    if not (user_is_sub and not user_is_busy and not user_is_weekend and user_is_work and not len(ActiveUserLinks) == 0):
        message += '\n\n<b>Парсер отключен:</b>'

        if not user_is_sub:
            message += '\n🔸 Нет подписки.'

        if not user_is_work:
            message += '\n🔸 Ваше рабочее время закончилось.'

        if user_is_weekend:
            message += '\n🔸 Ваш выходной день.'

        if user_is_busy:
            message += '\n🔸 Ваш статус "Занят".'

        if len(ActiveUserLinks) == 0:
            message += '\n🔸 Нет активных ссылок.'

    return message
