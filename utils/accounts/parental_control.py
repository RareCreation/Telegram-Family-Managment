import asyncio
from datetime import datetime
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from aiogram import Bot

from utils.console.logger_util import logger


async def check_parental_controls(bot: Bot):
    conn = sqlite3.connect("steam_accounts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, nickname, session_id, steam_login_secure FROM accounts")
    accounts = cursor.fetchall()
    conn.close()

    for user_id, nickname, session_id, steam_login_secure in accounts:
        try:
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--start-maximized")

            driver = webdriver.Chrome(options=options)

            try:
                driver.get("https://steampowered.com")
                driver.delete_all_cookies()
                driver.add_cookie({"name": "sessionid", "value": session_id, "domain": ".steampowered.com"})
                driver.add_cookie({"name": "steamLoginSecure", "value": steam_login_secure, "domain": ".steampowered.com"})

                driver.get("https://store.steampowered.com/account/familymanagement?tab=manage")

                WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "mz0H0iSlLfX7SQ7hv3kVY"))
                )

                panels = driver.find_elements(By.CLASS_NAME, "mz0H0iSlLfX7SQ7hv3kVY")

                for panel in panels[1:]:
                    try:
                        member_name_element = panel.find_element(By.CLASS_NAME, "nOdcT-MoOaXGePXLyPe0H")
                        member_name = member_name_element.text


                        dropdown_button = panel.find_element(By.CLASS_NAME, "_3Qa1urRRWR4tjkBSNaO8Wi")
                        dropdown_button.click()
                        await asyncio.sleep(2)

                    except Exception as e:
                        logger(f"[{nickname}]  Error processing panel{member_name}: {e}")
                        continue


                driver.execute_script("""
                document.querySelectorAll('div._2LyGIHuQ8SFKb5T262YUvg.Panel.Focusable').forEach(panel => {
                  const checkbox = panel.querySelector('div[role="checkbox"][aria-checked="true"]');
                  if (checkbox) {
                    panel.remove();
                  }
                });
                """)

                await asyncio.sleep(1)

                remaining_panels = driver.find_elements(By.CSS_SELECTOR, "div._2LyGIHuQ8SFKb5T262YUvg.Panel.Focusable")
                toggled_members = []
                if remaining_panels:

                    for panel in remaining_panels:
                        try:
                            checkbox = panel.find_element(By.CSS_SELECTOR, 'div[role="checkbox"]')
                            aria_checked = checkbox.get_attribute("aria-checked")
                            if aria_checked == "false":
                                checkbox.click()
                                member_name = panel.find_element(By.CLASS_NAME, "nOdcT-MoOaXGePXLyPe0H").text
                                toggled_members.append(member_name)
                        except Exception as e:
                            logger(f"Error when clicking on the panel:{e}")

                    if toggled_members:
                        for member in toggled_members:
                            await bot.send_message(user_id,
                                                   f"На аккаунте {nickname} включен род. контроль для пользователя {member}")
                    await asyncio.sleep(5)

                else:
                    logger(f"[{nickname}]")


            finally:
                driver.quit()

        except Exception as e:
            continue


async def periodic_check(bot: Bot):
    while True:
        await check_parental_controls(bot)
        await asyncio.sleep(60)
