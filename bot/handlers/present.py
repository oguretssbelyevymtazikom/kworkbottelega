from aiogram.types import CallbackQuery
from bot.app import dp
from bot.markup import markup
from models import user
from .menu import compose_menu_text


@dp.callback_query_handler(text_startswith='present')
async def callback_handler(call: CallbackQuery):
    user_id = call.from_user.id
    User = user.mark(user_id)

    if call.data == 'present':
        if User.subscription == 0:
            await call.answer('🎁 Активировано 3 дня подписки!', True)
            user.add_sub(user_id, 3)

        await call.message.edit_text(
            text=compose_menu_text(user_id),
            reply_markup=markup.menu(user_id)
        )
