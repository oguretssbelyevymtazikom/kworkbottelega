from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from models import user, link, referral, blacklist
from bot.app import SUB_YEAR_DISCOUNT, SUB_REFERRAL_DISCOUNT, SUPPORT_LINK
from bot.utils import get_sub_price


def menu(user_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Парсер', callback_data='parser')
    )
    markup.row(
        InlineKeyboardButton('💎', callback_data='subs'),
        InlineKeyboardButton('⚙', callback_data='settings'),
        InlineKeyboardButton('👥', callback_data='support')
    )

    User = user.mark(user_id)
    if User.subscription == 0:
        markup.add(
            InlineKeyboardButton('🎁 Забрать подарок', callback_data='present')
        )

    if User.status == 3:
        markup.add(
            InlineKeyboardButton('Админка', callback_data='admin')
        )

    return markup


def parser(user_id: int) -> InlineKeyboardMarkup:
    Links = link.get_all_by_owner(user_id)

    markup = InlineKeyboardMarkup()
    if Links:
        for Link in Links:
            markup.add(
                InlineKeyboardButton(f'{Link.name}', callback_data=f'parser.link.id.{Link.id}')
            )
    markup.row(
        InlineKeyboardButton('Назад', callback_data='menu'),
        InlineKeyboardButton('Добавить', callback_data='parser.add')
    )

    return markup


def parser_link(link_id: int) -> InlineKeyboardMarkup:
    Link = link.get(link_id)

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Отключить' if Link.active else 'Включить', callback_data=f'parser.link.toggle.{Link.id}')
    )
    markup.row(
        InlineKeyboardButton('Назад', callback_data='parser'),
        InlineKeyboardButton('Удалить', callback_data=f'parser.link.delete.{Link.id}')
    )

    return markup


def parser_add(user_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Отменить', callback_data='parser')
    )

    return markup


def refs(user_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Назад', callback_data='subs')
    )

    return markup


def subs(user_id: int) -> InlineKeyboardMarkup:
    is_referral = True if referral.get(user_id) else False
    price_30 = get_sub_price(user_id, 30)
    price_365 = get_sub_price(user_id, 365)

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        # InlineKeyboardButton(f'1 день - 13 руб.', callback_data='payment.pay.1'),
        InlineKeyboardButton(f'30 дней - {price_30} руб.' + (f' (-{SUB_REFERRAL_DISCOUNT}%)' if is_referral else ''), callback_data='payment.pay.30'),
        InlineKeyboardButton(f'365 дней - {price_365} руб. (-{SUB_YEAR_DISCOUNT}%)', callback_data='payment.pay.365'),
        InlineKeyboardButton(f'Бесплатная подписка', callback_data='subs.free')
    )
    markup.row(
        InlineKeyboardButton('Назад', callback_data='menu'),
        InlineKeyboardButton('Рефералка', callback_data='referral')
    )

    return markup


def support(user_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton('Назад', callback_data='menu'),
        InlineKeyboardButton('Написать', url=SUPPORT_LINK)
    )

    return markup


def alert(user_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton('Отправить', callback_data='alert.send'),
        InlineKeyboardButton('Удалить', callback_data='alert.delete')
    )

    return markup


def delete_call(user_id: int, button_text: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(button_text, callback_data='delete_call')
    )

    return markup


def admin(user_id: int, toggler: bool = True):
    markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton('Команды', callback_data='admin.commands')
    btn2 = InlineKeyboardButton('Статистика', callback_data='admin')
    markup.row(
        InlineKeyboardButton('Назад', callback_data='menu'),
        btn1 if toggler else btn2
    )

    return markup


def want(want_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton('Откликнуться', url=f'https://kwork.ru/new_offer?project={want_id}'),
        InlineKeyboardButton('Удалить', callback_data='delete_call')
    )

    return markup


def blacklist_menu(user_id: int) -> InlineKeyboardMarkup:
    Blacklists = blacklist.get_all_by_owner(user_id)

    markup = InlineKeyboardMarkup()
    if Blacklists:
        for Blacklist in Blacklists:
            markup.add(
                InlineKeyboardButton(f'{Blacklist.kwork_user_id}', callback_data=f'blacklist.delete.{Blacklist.id}')
            )
    markup.row(
        InlineKeyboardButton('Назад', callback_data='settings'),
        InlineKeyboardButton('Добавить', callback_data='blacklist.add')
    )

    return markup


def settings(user_id: int, User: user.UserModel) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton('Чёрный список', callback_data='blacklist'),
        InlineKeyboardButton('Шаблон сообщений', callback_data='settings.template')
    )
    markup.row(
        InlineKeyboardButton('Рабочее время', callback_data='settings.set_work_time'),
        InlineKeyboardButton('Выходные дни', callback_data='settings.set_weekends')
    )
    markup.row(
        InlineKeyboardButton('Назад', callback_data='menu'),
        InlineKeyboardButton('Занят' if User.busy else 'Свободен', callback_data='settings.busy')
    )

    return markup


def settings_back(user_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Назад', callback_data='settings')
    )

    return markup


def settings_template(user_id: int, toggler: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    if not toggler:
        markup.add(InlineKeyboardButton('Доступные теги', callback_data='settings.template.tags'))

    else:
        markup.add(InlineKeyboardButton('Текущий шаблон', callback_data='settings.template'))
    markup.add(
        InlineKeyboardButton('Назад', callback_data='settings'),
        InlineKeyboardButton('Сбросить', callback_data='settings.template.remove')
    )

    return markup


def blacklist_add(user_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Отменить', callback_data='blacklist')
    )

    return markup


def weekends(user_id: int, User: user.UserModel) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton('🔹 Пн' if '1' in User.weekends else 'Пн', callback_data='settings.set_weekends.1'),
        InlineKeyboardButton('🔹 Вт' if '2' in User.weekends else 'Вт', callback_data='settings.set_weekends.2'),
        InlineKeyboardButton('🔹 Ср' if '3' in User.weekends else 'Ср', callback_data='settings.set_weekends.3'),
        InlineKeyboardButton('🔹 Чт' if '4' in User.weekends else 'Чт', callback_data='settings.set_weekends.4')
    )
    markup.row(
        InlineKeyboardButton('🔹 Пт' if '5' in User.weekends else 'Пт', callback_data='settings.set_weekends.5'),
        InlineKeyboardButton('🔹 Сб' if '6' in User.weekends else 'Сб', callback_data='settings.set_weekends.6'),
        InlineKeyboardButton('🔹 Вс' if '7' in User.weekends else 'Вс', callback_data='settings.set_weekends.7')
    )
    markup.row(
        InlineKeyboardButton('Назад', callback_data='settings'),
    )

    return markup
