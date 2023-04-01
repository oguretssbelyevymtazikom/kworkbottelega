from aiogram.types import CallbackQuery
from bot.app import dp
from bot.markup import markup
from models import user


@dp.callback_query_handler(text_startswith='support')
async def callback_handler(call: CallbackQuery):
    user_id = call.from_user.id
    user.mark(user_id)

    await call.answer()

    if call.data == 'support':
        await call.message.edit_text(
            text=f'<b>Поддержка</b>\n\n'
                 f'Поддержка ответит на любой вопрос, касающийся бота. '
                 f'Так-же, поддержка принимает предложения по улучшению бота.\n\n'
                 f'Злоупотребление обращениями в поддержку, может привести к блокировке вашего аккаунта.\n\n'
                 f'Рабочее время поддержки, с 9:00 до 23:00 по МСК.',
            reply_markup=markup.support(user_id)
        )
