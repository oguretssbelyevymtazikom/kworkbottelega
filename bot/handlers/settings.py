import re
from aiogram.types import CallbackQuery, Message, ParseMode
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.app import dp, BLACKLIST_LIMIT
from bot.markup import markup
from models import user, blacklist


class WorkTime(StatesGroup):
    call_msg: Message = State()
    work_time: str = State()


class TemplateState(StatesGroup):
    call_msg: Message = State()
    text: str = State()


def compose_settings_text(user_id: int, User: user.UserModel):
    user_work_time = User.work_time if User.work_time else '24 часа'
    user_busy = 'Занят' if User.busy else 'Свободен'
    user_weekends = 'Нет'
    user_blacklist_length = len(blacklist.get_all_by_owner(user_id))
    user_template_is_default = user.template_is_default(user_id)

    if User.weekends != '0':
        user_weekends = ''
        weekend_days = ['', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

        for i in range(7):
            i = i+1
            if str(i) in User.weekends:
                if not user_weekends:
                    user_weekends += weekend_days[i]
                    continue

                user_weekends += f', {weekend_days[i]}'

    text = f'<b>Настройки бота</b>\n\n' \
           f'• Статус: <b>{user_busy}</b>\n' \
           f'• Рабочее время: <b>{user_work_time}</b>\n' \
           f'• Выходные дни: <b>{user_weekends}</b>\n' \
           f'• В чёрном списке: <b>{user_blacklist_length} / {BLACKLIST_LIMIT}</b>\n' \
           f'• Шаблон сообщений: <b>{"Стандартный" if user_template_is_default else "Пользовательский"}</b>'

    return text


def compose_template_text(User: user.UserModel, toggler: int):
    text = ''
    if toggler:
        text = f'<b>Изменение шаблона сообщений</b>\n\n' \
               f'Можете изменить шаблон получаемых от бота сообщений, на свой вкус, для большего удобства.\n\n' \
               f'<b>Доступные теги:</b>\n' \
               f'• Название ссылки: <code>[link_name]</code>\n' \
               f'• Заголовок предложения: <code>[title]</code>\n' \
               f'• Описание предложения: <code>[desc]</code>\n' \
               f'• Категория: <code>[cat]</code>\n' \
               f'• Родительская категория: <code>[parent_cat]</code>\n' \
               f'• Бюджет: <code>[budget]</code>\n' \
               f'• Допустимый бюджет: <code>[accept_budget]</code>\n' \
               f'• Имя пользователя (айди): <code>[user]</code>\n' \
               f'• Ссылка на пользователя: <code>[user_link]</code>\n' \
               f'• Процент найма: <code>[hired]</code>\n' \
               f'• Всего предложений: <code>[offers]</code>\n' \
               f'• Активных предложений: <code>[active_offers]</code>\n\n' \
               f'• Текст шаблона не более 500 символов.\n' \
               f'• Можно использовать HTML теги.\n\n' \
               f'🔸 Отправьте шаблон:'
        
    else:
        text = f'*Изменение шаблона сообщений*\n\n' \
               f'Можете изменить шаблон получаемых от бота сообщений, на свой вкус, для большего удобства\\.\n\n' \
               f'*Текущий шаблон:*\n`{User.template}`\n\n' \
               f'• Текст шаблона не более 500 символов\\.\n' \
               f'• Можно использовать HTML теги\\.\n\n' \
               f'🔸 Отправьте шаблон:'
        
    return text


@dp.callback_query_handler(text_startswith='settings', state='*')
async def callback_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    User = user.mark(user_id)

    if call.data == 'settings':
        if state:
            await state.finish()

        await call.message.edit_text(
            text=compose_settings_text(user_id, User),
            disable_web_page_preview=True,
            reply_markup=markup.settings(user_id, User)
        )

    elif call.data == 'settings.busy':
        User = user.toggle_busy(user_id)
        await call.answer('Получение сообщений отключено' if User.busy else 'Получение сообщений включено')
        await call.message.edit_text(
            text=compose_settings_text(user_id, User),
            disable_web_page_preview=True,
            reply_markup=markup.settings(user_id, User)
        )

    elif call.data == 'settings.set_work_time':
        await WorkTime.call_msg.set()
        async with state.proxy() as data:
            data['call_msg'] = call.message
            await WorkTime.next()

        await call.message.edit_text(
            text=f'<b>Установка рабочего времени</b>\n\n'
                 f'Сообщения о новых заказах будут приходить только в рабочее время. '
                 f'Установите промежуток времени, когда вы <b>хотите</b> '
                 f'получать уведомления о новых заказах.\n\n'
                 f'• Отправьте сообщение с промежутком времени.\n'
                 f'• Формат сообщения <b>8:00 - 19:35</b> (ОТ и ДО).\n'
                 f'• Для удаления рабочего времени, отправьте <b>0</b> (ноль)\n\n'
                 f'🔸 Укажите рабочее время:',
            disable_web_page_preview=True,
            reply_markup=markup.settings_back(user_id)
        )

    elif 'settings.template' in call.data:
        if call.data == 'settings.template':
            if not await state.get_state():
                await TemplateState.call_msg.set()
                async with state.proxy() as data:
                    data['call_msg'] = call.message
                    await TemplateState.next()

            await call.message.edit_text(
                text=compose_template_text(User, 0),
                disable_web_page_preview=True,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=markup.settings_template(user_id, 0)
            )

        elif call.data == 'settings.template.tags':
            await call.message.edit_text(
                text=compose_template_text(User, 1),
                disable_web_page_preview=True,
                reply_markup=markup.settings_template(user_id, 1)
            )

        elif call.data == 'settings.template.remove':
            if User.template != user.remove_tamplate(user_id):
                await call.answer('Установлен стандартный шаблон')
                await call.message.edit_text(
                    text=compose_template_text(User, 0),
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=markup.settings_template(user_id, 0)
                )

            await call.answer('Вы ещё не изменяли шаблон')

    elif 'settings.set_weekends' in call.data:
        if 'settings.set_weekends.' in call.data:
            weekend_day = call.data.split('.')[2]
            User = user.weekend(user_id, weekend_day)

        await call.message.edit_text(
            text=f'<b>Установка выходных дней</b>\n\n'
                 f'Сообщения о новых заказах <b>не будут</b> приходить в выходные дни.',
            disable_web_page_preview=True,
            reply_markup=markup.weekends(user_id, User)
        )

    await call.answer()


@dp.message_handler(state=WorkTime.work_time)
async def state_url(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    User = user.mark(user_id)

    if msg.text == '0':
        user.set_work_time(user_id, None)
        async with state.proxy() as data:
            await data['call_msg'].edit_text(
                text=compose_settings_text(user_id, User),
                disable_web_page_preview=True,
                reply_markup=markup.settings(user_id, User)
            )

            await state.finish()
            await msg.delete()

        return False

    if not re.match(r'^[\d]{1,2}\:[\d]{1,2}\-[\d]{1,2}\:[\d]{1,2}$', msg.text.replace(' ', '')):
        await msg.delete()
        return False

    async with state.proxy() as data:
        data['work_time'] = msg.text
        user.set_work_time(user_id, data['work_time'])

        await data['call_msg'].edit_text(
            text=compose_settings_text(user_id, User),
            disable_web_page_preview=True,
            reply_markup=markup.settings(user_id, User)
        )

        await state.finish()

    await msg.delete()


@dp.message_handler(state=TemplateState.text)
async def message_handler(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    User = user.mark(user_id)

    template_text = msg.text.strip()

    if len(template_text) > 500:
        await msg.delete()
        return False
    
    if template_text == User.template:
        await msg.delete()
        return False

    async with state.proxy() as data:
        data['text'] = template_text
        user.set_tamplate(user_id, template_text)

        await data['call_msg'].edit_text(
            text=compose_template_text(User, 0),
            disable_web_page_preview=True,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=markup.settings_template(user_id, 0)
        )

    await msg.delete()
