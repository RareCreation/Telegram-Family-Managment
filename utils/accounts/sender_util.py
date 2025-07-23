import asyncio
import sqlite3
from utils.accounts.parental_control import parental_control_async
from aiogram import Bot
from utils.console.logger_util import logger

async def checker(bot: Bot):
    while True:
        conn = sqlite3.connect("steam_accounts.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_id, nickname, session_id, steam_login_secure FROM accounts")
        accounts = cursor.fetchall()
        conn.close()

        for account in accounts:
            acc_id, user_id, nickname, session_id, steam_login_secure = account
            try:
                messages = await parental_control_async(session_id, steam_login_secure, nickname)
                if messages:
                    for msg in messages:
                        await bot.send_message(user_id, msg)
            except Exception as e:
                logger(f"Account verification error {nickname}: {e}")

        await asyncio.sleep(20)
