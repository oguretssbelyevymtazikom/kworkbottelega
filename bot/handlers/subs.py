from aiogram.types import CallbackQuery
from bot.app import dp, scheduler
from bot.markup import markup
from models import user, payment


@dp.callback_query_handler(text_startswith='subs')
async def callback_handler(call: CallbackQuery):
    user_id = call.from_user.id
    user.mark(user_id)

    UserUnactivePayments = payment.get_all_unactive_by_client(user_id)
    if UserUnactivePayments:
        for UserUnactivePayment in UserUnactivePayments:
            try:
                scheduler.remove_job(UserUnactivePayment.payment_id)
            except:
                pass
            finally:
                payment.delete(UserUnactivePayment.payment_id)

    if call.data == 'subs':
        await call.message.edit_text(
            text=f'<b>Оформление подписки</b>\n\n'
                 f'Пользователи с подпиской, могут использовать весь функционал бота, в полном объёме.\n\n'
                 f'• Текущая подписка: <b>{user.get_sub_string(user_id)}</b>',
            disable_web_page_preview=True,
            reply_markup=markup.subs(user_id)
        )

    elif call.data == 'subs.free':
        await call.answer(
            text=f'⭐ Бесплатная подписка\n\n'
                 f'Бот работает в режиме тестирования. '
                 f'Сообщите в поддержку, если найдёте баг или недоработку, '
                 f'и мы выдадим вам до 30 дней подписки.',
            show_alert=True
        )

    await call.answer()
