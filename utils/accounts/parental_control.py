from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import asyncio


from utils.console.logger_util import logger


def parental_control(session_id: str, steam_login_secure: str, nickname: str) -> list[str]:
    messages = []
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    try:
        driver.get("https://steampowered.com")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        driver.delete_all_cookies()
        driver.add_cookie({"name": "sessionid", "value": session_id, "domain": ".steampowered.com"})
        driver.add_cookie({"name": "steamLoginSecure", "value": steam_login_secure, "domain": ".steampowered.com"})

        driver.get("https://store.steampowered.com/account/familymanagement?tab=manage")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div._2VcTlXFC64Jtg9gvtT6cmY")))

        user_blocks = driver.find_elements(By.CSS_SELECTOR, "div._2VcTlXFC64Jtg9gvtT6cmY")
        for user_block in user_blocks:
            try:
                username = user_block.find_element(By.CSS_SELECTOR, "div._3jMlJm4PQCA8SfNlUR99Fo").text.strip()
                checkbox_div = user_block.find_element(By.CSS_SELECTOR, "div[role='checkbox']")
                aria_checked = checkbox_div.get_attribute("aria-checked")
                if aria_checked == "false":
                    checkbox_div.click()
                    messages.append(f"На аккаунте {nickname} включен родительский контроль для пользователя {username}")
                    time.sleep(2)
            except Exception as e:
                logger(f"Error processing user in account {nickname}: {e}")

        return messages

    except Exception as e:
        logger(f"Account verification error {nickname}: {e}")
        return []

    finally:
        driver.quit()

