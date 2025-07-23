import asyncio
from handlers.bot_instance import dp, bot
from routers import start
from utils.accounts.sender_util import checker
from utils.console.logger_util import logger
from utils.setup_commands.setup_bot_commands import setup_bot_commands


async def main():
    logger("Bot has been loaded")
    await setup_bot_commands(bot)
    dp.include_router(start.router)
    asyncio.create_task(checker(bot))
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())
