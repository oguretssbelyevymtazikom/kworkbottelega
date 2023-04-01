from aiogram.utils import executor
from bot.app import dp, shutdown, scheduler
import models
import bot


if __name__ == '__main__':
    scheduler.add_job(models.want.delete_old, 'interval', hours=1)
    scheduler.start()
    executor.start_polling(
        dispatcher=dp,
        skip_updates=True,
        on_shutdown=shutdown
    )
