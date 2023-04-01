# Other
import time
from datetime import datetime
from yookassa import Configuration
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Telegram Bot API
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode, CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage


BOT_TOKEN = '5290580329:AAFV3VR-aJVfy2nNV00zaqMbWt9WIYIxyBc'
BOT_USERNAME = 'kwrk_bot'
BOT_ROOT_ID = 874620151

Configuration.account_id = 203696
Configuration.secret_key = 'test_LlGpENO07DN0o5G59pAkJaLy2HDTDWNyxlVFl_1Ga6I'

PAYMAN_FULLNAME = 'Финченко Даниил Николаевич'
PAYMAN_INN = '503911614570'
PAYMAN_EMAIL = 'fidani@gmail.com'
PAYMAN_PHONE = '78005553535'

SUPPORT_LINK = 'https://t.me/kwrk_support'
SUPPORT_ID = 1438085639

SUB_DAY_PRICE = 11
SUB_YEAR_DISCOUNT = 21
SUB_REFERRAL_DISCOUNT = 15

REF_GIFT_DAYS = 3
REF_ULTRA_GIFT_DAYS = 30

PARSER_LINKS_LIMIT = 5

BLACKLIST_LIMIT = 10


# Create Bot
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

# Scheduler
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')


def get_time() -> int:
    """Возвращает Московское время с начала эпохи"""
    utc_time = time.time()
    moscow_time = utc_time + 10800
    return int(moscow_time)


def get_datetime(time: int) -> datetime:
    """Конвертирует get_time() в дату."""
    return datetime.utcfromtimestamp(time)


def is_work_time(from_hour: int, from_min: int, to_hour: int, to_min: int) -> bool:
    """Определяет, рабочее ли сейчас время"""
    date = get_datetime(get_time()).strftime('%Y-%m-%d')
    year, month, day = map(int, date.split('-'))
    if datetime(year, month, day, from_hour, from_min, 0, 0) < datetime.now() < datetime(year, month, day, to_hour, to_min, 0, 0):
        return True
    
    return False


async def logger(status: int, location: str, message: str, exception: str, user_id: int = None):
    # markup = InlineKeyboardMarkup()
    # markup.add(
        # InlineKeyboardButton('Тех. работы', callback_data='logger.twork')
    # )

    await bot.send_message(
        chat_id=SUPPORT_ID,
        text=f'🔸 <b>Ошибка. Уровень {status}</b>\n\n'
             f'• Инициатор: <b><code>{user_id if user_id else "Нет"}</code></b>\n'
             f'• Сообщение: <b><code>{message}</code></b>\n'
             f'• Локация: <b><code>{location}</code></b>\n'
             f'• Исключение: <b><code>{exception}</code></b>',
        disable_web_page_preview=True,
        protect_content=True,
        # reply_markup=markup
    )
    

@dp.callback_query_handler(text_startswith='logger')
async def callback_handler(call: CallbackQuery):
    user_id = call.from_user.id
    if call.data == 'logger.twork':
        await call.answer(f'🔹 Бот переведён на тех. работы.\n🔹 Root пользователь уведомлён.', True)
        await call.message.delete()


# On Shutdown Bot
async def shutdown(dispatcher: Dispatcher):
    scheduler.remove_all_jobs()
    await dispatcher.storage.close()
    # await dispatcher.bot.close() TODO: Удалить на проде.
