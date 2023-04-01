from aiogram.types import CallbackQuery
from bot.app import dp
from bot.markup import markup
from models import referral, user


@dp.callback_query_handler(text_startswith='referral')
async def callback_handler(call: CallbackQuery):
    user_id = call.from_user.id
    user.mark(user_id)

    Referrals = referral.get_all_by_owner(user_id)
    ActiveReferrals = referral.get_all_active_by_owner(user_id)
    refs_string = '• Ваши рефералы: '

    await call.answer()

    if Referrals:
        refs_string += f'<b>{len(ActiveReferrals)} активных, из {len(Referrals)}</b>'
    else:
        refs_string += 'Нет'

    await call.message.edit_text(
        text=f'<b>Реферальная система</b>\n\n'
             f'1. Приглашайте пользователей, по реферальной ссылке.\n'
             f'2. Каждый активный реферал приносит вам <b>+3 дня</b> подписки.\n'
             f'3. Рефералы получают <b>скидку 15%</b> на оплату подписки.\n'
             f'4. За каждые 10 активных рефералов вы получаете <b>+30 дней</b> подписки.\n'
             f'5. Рефералы становятся активными, после оплаты подписки.\n\n'
             f'{refs_string}\n'
             f'• Ваша ссылка: <code>https://t.me/kwrk_bot?start=ref-{user_id}</code> (Нажмите, чтобы скопировать)\n',
        disable_web_page_preview=True,
        reply_markup=markup.refs(user_id)
    )
