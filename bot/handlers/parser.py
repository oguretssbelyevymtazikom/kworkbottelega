from datetime import datetime
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.app import dp, PARSER_LINKS_LIMIT, get_datetime
from bot.markup import markup
from models import user, link


class ParseLink(StatesGroup):
    call_msg = State()
    name = State()
    url = State()


def compose_parser_text(user_id: int):
    text = f'<b>Настройка парсера</b>\n\n' \
           f'1. Перейдите по <a href="https://kwork.ru/projects?c=all">ссылке</a>.\n' \
           f'2. Настройте фильтры.\n' \
           f'3. Скопируйте URL из адресной строки.\n' \
           f'4. Добавьте скопированный URL в бота.\n\n' \
           f'Не добавляйте ссылку из рубрики "Любимые", перед настройкой фильтров, перейдите в рубрику "Все".\n\n' \
           f'При возникновении любых трудностей - обращайтесь в поддержку.'
    
    return text


def validate_url(user_id: int, url: str) -> bool:
    url = url.strip()

    if len(url) >= 500:
        return False

    if 'https://kwork.ru/projects' not in url[:25]:
        return False
    
    if link.get_by_owner_url(user_id, url):
        return False 
    
    return True


def validate_name(user_id: int, name: str) -> bool:
    if len(name.encode()) > 32:
        return False
    
    if link.get_by_owner_name(user_id, name):
        return False
    
    return True


@dp.message_handler(state=ParseLink.name)
async def state_url(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    user.mark(user_id)

    if not validate_name(user_id, msg.text):
        await msg.delete()
        return False

    async with state.proxy() as data:
        data['name'] = msg.text
        await data['call_msg'].edit_text(
            text=f'<b>Добавление ссылки</b>\n\n'
                 f'<b>Ссылку</b> можно получить на сайте, '
                 f'перейдите на вкладку "Биржа", установите необходимые фильтры, '
                 f'а затем, скопируйте ссылку и отправьте сюда.\n\n'
                 f'• Ссылки не должны повторяться.\n'
                 f'• Ссылка должна начинаться с https://kwork.ru/projects\n'
                 f'• Не отправляйте ссылку из рубрики "Любимые".\n\n'
                 f'🔸 Отправьте ссылку:',
            disable_web_page_preview=True,
            reply_markup=markup.parser_add(user_id)
        )

        await ParseLink.next()

    await msg.delete()


@dp.message_handler(state=ParseLink.url)
async def state_url(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    user.mark(user_id)

    if not validate_url(user_id, msg.text):
        await msg.delete()
        return False

    async with state.proxy() as data:
        data['url'] = msg.text

        link.create(user_id, data['name'], data['url'])

        await data['call_msg'].edit_text(
            text=compose_parser_text(user_id),
            disable_web_page_preview=True,
            reply_markup=markup.parser(user_id)
        )

        await state.finish()

    await msg.delete()
    

@dp.callback_query_handler(text_startswith='parser', state='*')
async def callback_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    user.mark(user_id)

    if call.data == 'parser':
        if state:
            await state.finish()

        try:
            await call.message.edit_text(
                text=compose_parser_text(user_id),
                disable_web_page_preview=True,
                reply_markup=markup.parser(user_id)
            )
        except:
            pass

    elif call.data == 'parser.add':
        Links = link.get_all_by_owner(user_id)
        if len(Links) >= PARSER_LINKS_LIMIT:
            return await call.answer(
                text=f'Превышен лимит активных ссылок 😢',
                show_alert=True
            )

        await ParseLink.call_msg.set()
        async with state.proxy() as data:
            data['call_msg'] = call.message
            await ParseLink.next()

        await call.message.edit_text(
            text=f'<b>Добавление ссылки</b>\n\n'
                 f'<b>Название</b> ссылки нужно только для вас. '
                 f'Постарайтесь придумать такое название, чтобы сразу понимать, '
                 f'за парсинг каких заказов отвечает эта ссылка.\n\n'
                 f'• Названия ссылок не должны повторяться.\n\n'
                 f'🔸 Отправьте <b>название</b> ссылки:',
            disable_web_page_preview=True,
            reply_markup=markup.parser_add(user_id)
        )

    elif 'parser.link.toggle.' in call.data:
        link_id = int(call.data.split('.')[3])
        Link = link.toggle(link_id)
        link_date = get_datetime(Link.creation_time)
        link_date_format = datetime.strftime(link_date, '%Y.%m.%d - %H:%M:%S')

        await call.message.edit_text(
            text=f'Название: <b>{Link.name}</b>\n'
                 f'Ссылка: <b>{Link.url}</b>\n'
                 f'Дата создания: <b>{link_date_format}</b>\n',
            disable_web_page_preview=True,
            reply_markup=markup.parser_link(link_id)
        )

    elif 'parser.link.delete.' in call.data:
        link_id = int(call.data.split('.')[3])
        link.delete(link_id)

        await call.message.edit_text(
            text=compose_parser_text(user_id),
            disable_web_page_preview=True,
            reply_markup=markup.parser(user_id)
        )

    elif 'parser.link.id.' in call.data:
        link_id = int(call.data.split('.')[3])
        Link = link.get(link_id)
        link_date = get_datetime(Link.creation_time)
        link_date_format = datetime.strftime(link_date, '%Y.%m.%d - %H:%M:%S')

        await call.message.edit_text(
            text=f'Название: <b>{Link.name}</b>\n'
                 f'Ссылка: <b>{Link.url}</b>\n'
                 f'Дата создания: <b>{link_date_format}</b>\n',
            disable_web_page_preview=True,
            reply_markup=markup.parser_link(link_id)
        )
    
    await call.answer()
