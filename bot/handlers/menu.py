from aiogram.types import Message, CallbackQuery
from models import user, referral, message, payment
from bot.app import bot, dp, scheduler, SUB_REFERRAL_DISCOUNT
from bot.markup import markup
from bot.utils import send_message, compose_menu_text


async def create_referral(referrer_id: int, referral_id: int):
    try:
        if referrer_id == referral_id:
            return False

        if not user.get(referrer_id):
            return False

        if user.get(referral_id):
            return False
        
        if referral.get(referral_id):
            return False
        
        Referral = referral.create(referrer_id, referral_id)
        return Referral if Referral else False

    except Exception as ex:
        print(ex)

    return False


@dp.message_handler(commands=['start', 'clear', 'menu'])
async def command_start(msg: Message):
    user_id = msg.from_user.id

    is_referral = False
    if 'start ref-' in msg.text:
        Referral = await create_referral(int(msg.text.split('-')[1]), user_id)
        if Referral:
            is_referral = True

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

    await msg.delete()
    menu_message = await send_message(
        chat_id=user_id,
        text=compose_menu_text(user_id),
        reply_markup=markup.menu(user_id)
    )

    if is_referral:
        await bot.send_message(
            chat_id=user_id,
            text=f'💎 Вы перешли по реферальной ссылке!\n\n'
                 f'В течении трёх дней будет действовать <b>скидка {SUB_REFERRAL_DISCOUNT}%</b> '
                 f'на покупку <b>30-ти</b> дней подписки.\n\n'
                 f'Подробнее о реферальной системе - в меню "Подписка".',
            reply_markup=markup.delete_call(user_id, 'Отлично!')
        )

    Messages = message.get_all_by_user(user_id)
    for Message in Messages:
        if Message.message_id == menu_message.message_id:
            continue

        try:
            await bot.delete_message(Message.user_id, Message.message_id)
        except:
            pass

        finally:
            message.delete(Message.user_id, Message.message_id)


@dp.callback_query_handler(text_startswith='menu')
async def callback_handler(call: CallbackQuery):
    user_id = call.from_user.id
    user.mark(user_id)

    await call.answer()

    if call.data == 'menu':
        await call.message.edit_text(
            text=compose_menu_text(user_id),
            reply_markup=markup.menu(user_id)
        )
