import asyncio
from handlers.bot_instance import dp, bot
from routers import start
from utils.accounts.parental_control import periodic_check
from utils.console.logger_util import logger
from utils.setup_commands.setup_bot_commands import setup_bot_commands


async def on_startup(dispatcher):
    logger("Bot startup initiated")
    logger("Starting periodic check task...")
    asyncio.create_task(periodic_check(bot))
    logger("Periodic check task started")


async def main():
    logger("Bot has been loaded")

    dp.startup.register(on_startup)

    await setup_bot_commands(bot)
    dp.include_router(start.router)

    logger("Starting bot polling...")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    logger("Launching bot application...")
    asyncio.run(main())