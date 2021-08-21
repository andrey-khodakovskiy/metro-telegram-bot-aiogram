import asyncio

import logging
from decouple import config

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.handlers.main import register_handlers_main
from app.handlers.common import register_handlers_common


logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.WARNING)

BOT_TOKEN = config("BOT_TOKEN")


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать работу"),
        BotCommand(command="/exit", description="Завершить работу"),
        BotCommand(command="/restart", description="Начать заново"),
    ]
    await bot.set_my_commands(commands)


async def main():

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[console],
    )
    logger.error("Starting bot")

    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_handlers_common(dp)
    register_handlers_main(dp)

    await set_commands(bot)
    await dp.skip_updates()
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
