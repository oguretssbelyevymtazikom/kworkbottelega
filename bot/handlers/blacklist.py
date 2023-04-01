from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.app import dp, BLACKLIST_LIMIT
from bot.markup import markup
from models import user, blacklist


class BlacklistState(StatesGroup):
    call_msg = State()
    kwork_user_id = State()


def compose_blacklist_text():
    text = f'<b>Чёрный список заказчиков</b>\n\n' \
           f'Добавляйте заказчиков в чёрный список, если ' \
           f'не желаете получать уведомления о их заказах.\n\n' \
           f'Нажмите на заказчика, для удаления.'
    
    return text


def validate_url(user_id: int, url: str) -> bool:
    url = url.strip()

    if len(url) >= 500 or len(url) <= 22:
        return False

    if 'https://kwork.ru/user/' not in url[:22]:
        return False
    
    kwork_user_id = url[22:]

    if not kwork_user_id:
        return False

    if len(kwork_user_id) > 32:
        return False
    
    if blacklist.get_by_owner(user_id, kwork_user_id):
        return False 
    
    return True


@dp.message_handler(state=BlacklistState.kwork_user_id)
async def state_url(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    user.mark(user_id)

    if not validate_url(user_id, msg.text):
        await msg.delete()
        return False

    async with state.proxy() as data:
        data['kwork_user_id'] = msg.text[22:].lower()

        blacklist.create(user_id, data['kwork_user_id'])

        await data['call_msg'].edit_text(
            text=compose_blacklist_text(),
            disable_web_page_preview=True,
            reply_markup=markup.blacklist_menu(user_id)
        )

        await state.finish()

    await msg.delete()


@dp.callback_query_handler(text_startswith='blacklist', state='*')
async def callback_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    user.mark(user_id)

    if call.data == 'blacklist':
        if state:
            await state.finish()

        await call.message.edit_text(
            text=compose_blacklist_text(),
            reply_markup=markup.blacklist_menu(user_id)
        )
    
    elif call.data == 'blacklist.add':
        Blacklists = blacklist.get_all_by_owner(user_id)
        if len(Blacklists) >= BLACKLIST_LIMIT:
            return await call.answer(
                text=f'Превышен лимит 😢',
                show_alert=True
            )

        await BlacklistState.call_msg.set()
        async with state.proxy() as data:
            data['call_msg'] = call.message
            await BlacklistState.next()
        
        await call.message.edit_text(
            text=f'<b>Добавление в чёрный список</b>\n\n'
                 f'🔸 Отправьте ссылку на пользователя Kwork:',
            reply_markup=markup.blacklist_add(user_id)
        )

    elif 'blacklist.delete.' in call.data:
        Blacklist_id = call.data.split('.')[2]
        blacklist.delete(Blacklist_id)

        await call.message.edit_text(
            text=compose_blacklist_text(),
            disable_web_page_preview=True,
            reply_markup=markup.blacklist_menu(user_id)
        )
    
    await call.answer()
