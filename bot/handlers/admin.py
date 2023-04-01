from aiogram.types import Message, CallbackQuery
from models import user, referral, message, blacklist, payment, link, want
from bot.app import bot, dp
from bot.markup import markup
from bot.utils import send_message


async def command_message(user_id: int, target_id: int, user_message: str, target_message: str):
    await bot.send_message(
        chat_id=user_id,
        text=user_message,
        reply_markup=markup.delete_call(user_id, 'Окей')
    )

    await bot.send_message(
        chat_id=target_id,
        text=target_message,
        reply_markup=markup.delete_call(target_id, 'Окей')
    )


@dp.message_handler(commands=['delwants'])
@user.user_status(3)
async def message_handler(msg: Message):
    user_id = msg.from_user.id
    user.mark(user_id)

    deleted = want.delete_old()
    await msg.answer(f'Удалено {deleted} предложений.')


@dp.message_handler(commands=['permdelete'])
@user.user_status(3)
async def message_handler(msg: Message):
    user_id = msg.from_user.id
    user.mark(user_id)

    if len(msg.text.split(' ')) == 2:
        try:
            target_id = msg.text.split(' ')[1]
            target_id = int(target_id)

            user.delete(target_id)
            
            Payments = payment.get_all_by_client(target_id)
            if Payments:
                for Payment in Payments:
                    payment.delete(Payment.payment_id)
            
            Links = link.get_all_by_owner(target_id)
            if Links:
                for Link in Links:
                    link.delete(Link.id)

            Referrals = referral.get_all_by_owner(target_id)
            if Referrals:
                for Referral in Referrals:
                    referral.delete(Referral.referral_id)

            Blacklists = blacklist.get_all_by_owner(target_id)
            if Blacklists:
                for Blacklist in Blacklists:
                    blacklist.delete(Blacklist.id)

            Messages = message.get_all_by_user(target_id)
            if Messages:
                for Message in Messages:
                    message.delete(target_id, Message.message_id)

            await msg.answer('Пользователь удалён.')

        except:
            pass
        


@dp.message_handler(commands=['clearsub'])
@user.user_status(3)
async def message_handler(msg: Message):
    user_id = msg.from_user.id
    user.mark(user_id)
    
    if len(msg.text.split(' ')) == 2:
        try:
            target_id = msg.text.split(' ')[1]
            target_id = int(target_id)

            user.clear_sub(target_id)

            await command_message(
                user_id=user_id,
                target_id=target_id,
                user_message=f'Пользователю <code>{target_id}</code> обнулена подписка.',
                target_message=f'Администратор обнулил вашу подписку.'
            )

        except Exception as ex:
            print(ex)

    else:
        await send_message(
            chat_id=user_id,
            text=f'Используйте: <code>/clearsub user_id</code>',
            reply_markup=markup.delete_call(user_id, 'Окей')
        )


@dp.message_handler(commands=['status'])
@user.user_status(3)
async def message_handler(msg: Message):
    user_id = msg.from_user.id
    user.mark(user_id)
    
    if len(msg.text.split(' ')) == 3:
        try:
            _, target_id, status = msg.text.split(' ')
            target_id = int(target_id)
            status = int(status)

            user.set_status(target_id, status)

            await command_message(
                user_id=user_id,
                target_id=target_id,
                user_message=f'Пользователю <code>{target_id}</code> установлен статус {status}.',
                target_message=f'Администратор установил вам новый статус: {status}.'
            )

        except Exception as ex:
            print(ex)

    else:
        await send_message(
            chat_id=user_id,
            text=f'Используйте: <code>/status user_id status</code>',
            reply_markup=markup.delete_call(user_id, 'Окей')
        )


@dp.message_handler(commands=['sub'])
@user.user_status(3)
async def message_handler(msg: Message):
    user_id = msg.from_user.id
    user.mark(user_id)
    
    if len(msg.text.split(' ')) == 3:
        try:
            command, target_id, sub_days = msg.text.split(' ')
            target_id = int(target_id)
            sub_days = int(sub_days)

            if not sub_days:
                return False

            elif sub_days > 0:
                await command_message(
                    user_id=user_id,
                    target_id=target_id,
                    user_message=f'Пользователю <code>{target_id}</code> добавлено +{sub_days} д. подписки.',
                    target_message=f'🎁 Администратор добавил вам +{sub_days} д. подписки.'
                )

            else:
                await command_message(
                    user_id=user_id,
                    target_id=target_id,
                    user_message=f'Вы отняли {sub_days} д. подписки у пользователя <code>{target_id}</code>.',
                    target_message=f'🎁 Администратор отнял у вас {sub_days} д. подписки.'
                )

            user.add_sub(target_id, sub_days)

        except Exception as ex:
            print(ex)

    else:
        await bot.send_message(
            chat_id=user_id,
            text=f'Используйте: <code>/sub user_id days</code>',
            reply_markup=markup.delete_call(user_id, 'Окей')
        )


@dp.message_handler(commands=['alert'])
@user.user_status(3)
async def message_handler(msg: Message):
    user_id = msg.from_user.id
    user.mark(user_id)

    message_text = msg.html_text.replace('/alert', '').strip()

    if message_text:
        await bot.send_message(
            chat_id=user_id,
            text=message_text,
            reply_markup=markup.alert(user_id)
        )

    else:
        await bot.send_message(
            chat_id=user_id,
            text=f'Использование: <code>/alert message</code>\n\n'
                 f'Можно использовать HTML разметку.',
            reply_markup=markup.delete_call(user_id, 'Окей')
        )


@dp.callback_query_handler(text_startswith='alert')
@user.user_status(3)
async def callback_handler(call: CallbackQuery):
    user_id = call.from_user.id
    
    Users = user.get_all()

    if call.data == 'alert.send':
        sended = 0

        for User in Users:
            if User.user_id != user_id:
                try:
                    await bot.send_message(
                        chat_id=User.user_id,
                        text=call.message.text.replace('/alert ', ''),
                        disable_web_page_preview=True,
                        reply_markup=markup.delete_call(user_id, 'Прочитано')
                    )

                    sended += 1

                except:
                    user.set_active(user_id, False)

        await call.answer(
            text=f'{sended} из {len(Users) - 1} пользователей\nполучили ваше сообщение.',
            show_alert=True
        )

        await call.message.delete()

    if call.data == 'alert.delete':
        await call.message.delete()
        await call.answer()


@dp.callback_query_handler(text_startswith='delete_call', state='*')
async def callback_handler(call: CallbackQuery):
    user_id = call.from_user.id
    user.mark(user_id)

    try:
        await call.message.delete()
        MessageModel = message.get(user_id, call.message.message_id)
        if MessageModel:
            message.delete(user_id, call.message.message_id)
    except:
        pass


@dp.callback_query_handler(text_startswith='admin')
@user.user_status(3)
async def callback_handler(call: CallbackQuery):
    user_id = call.from_user.id
    user.mark(user_id)
    
    if call.data == 'admin':
        Users = user.get_all()
        ActiveUsers = user.get_all_active_on_time(seconds=10 * 86400)
        Referrals = referral.get_all()
        ActiveReferrals = referral.get_all_active()
        SubUsers = user.get_all_on_sub()

        TopReferrer = {'referrer_id': None, 'amount': 0}
        for Referral in Referrals:
            OwnerReferrals = referral.get_all_by_owner(Referral.referrer_id)

            if not TopReferrer['referrer_id']:
                TopReferrer['referrer_id'] = Referral.referrer_id
                TopReferrer['amount'] = len(OwnerReferrals)
                continue

            if len(OwnerReferrals) > TopReferrer['amount']:
                TopReferrer['referrer_id'] = Referral.referrer_id
                TopReferrer['amount'] = len(OwnerReferrals)

        users = len(Users)
        active_users = len(ActiveUsers)
        referrals = len(Referrals)
        active_referrals = len(ActiveReferrals)
        sub_users = len(SubUsers)

        await call.message.edit_text(
            text=f'<b>Статистика бота</b>\n\n'
                 f'• Активных пользователей: <b>{active_users} / {users}</b>\n'
                 f'• Пользователей с подпиской: <b>{sub_users} / {users}</b>\n'
                 f'• Активных рефералов: <b>{active_referrals} / {referrals}</b>\n'
                 f'• Топ реферер: <b><code>{TopReferrer["referrer_id"]}</code> - {TopReferrer["amount"]}</b>',
            reply_markup=markup.admin(user_id, True)
        )

    elif call.data == 'admin.commands':
        await call.message.edit_text(
            text=f'<b>Команды администратора</b>\n\n'
                 f'• <code><b>/sub user_id days</b></code> - прибавить дни подписки.\n'
                 f'• <code><b>/resub user_id days</b></code> - отнять дни подписки.\n'
                 f'• <code><b>/clearsub user_id</b></code> - обнулить подписку.\n'
                 f'• <code><b>/alert message</b></code> - уведомление пользователей.\n'
                 f'• <code><b>/status user_id status</b></code> - установить статус.\n'
                 f'• <code><b>/ban user_id</b></code> - заблокировать пользователя.\n'
                 f'• <code><b>/unban user_id</b></code> - разблокировать пользователя.\n'
                 f'• <code><b>/msg user_id message</b></code> - сообщение пользователю.\n'
                 f'• <code><b>/ref referrer_id referral_id</b></code> - назначить реферала.\n',
            reply_markup=markup.admin(user_id, False)
        )
