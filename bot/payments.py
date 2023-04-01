from yookassa import Payment
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from .app import bot, dp, scheduler, REF_GIFT_DAYS, REF_ULTRA_GIFT_DAYS
from .utils import get_sub_price, create_payment, compose_menu_text, send_message
from models import user, payment, referral
from .markup import markup


async def check_payment(user_id: int, payment_id: str, call: CallbackQuery):
    try:
        PaymentResponse = Payment.find_one(payment_id)

        if PaymentResponse.status == 'succeeded':
            scheduler.remove_job(PaymentResponse.id)
            PaymentModel = payment.complete(PaymentResponse.id)

            user.add_sub(user_id, PaymentModel.amount)

            Referral = referral.get(user_id)
            if Referral:
                Referral = referral.activate(user_id)
                ReferrerActiveReferrals = referral.get_all_active_by_owner(Referral.referrer_id)
                referrals_count = len(ReferrerActiveReferrals)

                referrer_gift_days = 0
                
                if referrals_count and int(str(referrals_count)[-1:]) == 0:
                    referrer_gift_days = REF_ULTRA_GIFT_DAYS
                else:
                    referrer_gift_days = REF_GIFT_DAYS

                user.add_sub(Referral.referrer_id, referrer_gift_days)

                await bot.send_message(
                    chat_id=Referral.referrer_id,
                    text=f'💎 Вы получил +{referrer_gift_days} д. подписки, за реферала.',
                    reply_markup=markup.delete_call(Referral.referrer_id, 'Отлично!')
                )

            await call.message.edit_text(
                text=compose_menu_text(user_id),
                reply_markup=markup.menu(user_id)
            )

            await bot.send_message(
                chat_id=user_id,
                text=f'💎 Получено +{PaymentModel.amount} дней подписки!',
                reply_markup=markup.delete_call(user_id, 'Отлично!')
            )

    except Exception as ex:
        scheduler.remove_job(PaymentResponse.id)
        print(ex)


@dp.callback_query_handler(text_startswith='payment')
async def callback_handler(call: CallbackQuery):
    user_id = call.from_user.id
    user.mark(user_id)

    if 'payment.pay.' in call.data:
        try:
            sub_days = int(call.data.split('.')[2])
            sub_price = get_sub_price(user_id, sub_days)

            PaymentResponse = create_payment(user_id, sub_price, f'Kwork Notifier | {sub_days} д. подписки')

            payment.create(user_id, PaymentResponse.id, sub_days, sub_price)

            payment_markup = InlineKeyboardMarkup()
            payment_markup.row(
                InlineKeyboardButton('Назад', callback_data=f'subs'),
                InlineKeyboardButton('Оплатить', url=PaymentResponse.confirmation.confirmation_url)
            )

            await call.message.edit_text(
                text=f'💎 <b>Оплата +{sub_days} д. подписки, за {sub_price} руб.</b>\n\n'
                     f'Для оплаты вы будете перенаправлены на сайт YOOKASSA. '
                     f'Подписка начисляется моментально, после успешной оплаты.\n\n'
                     f'Через поддержку доступна оплата любым способом.',
                reply_markup=payment_markup
            )

            scheduler.add_job(check_payment, 'interval', id=PaymentResponse.id, seconds=1, kwargs={'user_id': user_id, 'payment_id': PaymentResponse.id, 'call': call})

        except Exception as ex:
            await call.answer('Что-то пошло не так\n\nАдминистрация уведомлена. Приносим извинения.', show_alert=True)
            print(ex)

    await call.answer()
