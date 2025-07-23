import sqlite3
import io
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
async def run_selenium_check(session_id: str, steam_login_secure: str) -> tuple[str, str]:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://steampowered.com")
        time.sleep(1)
        driver.delete_all_cookies()
        driver.add_cookie({"name": "sessionid", "value": session_id, "domain": ".steampowered.com"})
        driver.add_cookie({"name": "steamLoginSecure", "value": steam_login_secure, "domain": ".steampowered.com"})

        driver.get("https://store.steampowered.com/account/familymanagement?tab=manage")
        time.sleep(5)

        elements = driver.find_elements(By.CLASS_NAME, "_3ayYOCw_ZCm0rF1vDVmwfO")
        nickname = extract_nickname(driver)

        if any("Focusable" in e.get_attribute("class") for e in elements):
            return nickname, f"✅ Успешно: аккаунт {nickname} добавлен."
        else:
            return nickname, f"⚠️ Аккаунт {nickname} загружен, но элемент не найден."

    except Exception as e:
        return "", f"❌ Ошибка: {e}"
    finally:
        driver.quit()

def extract_nickname(driver) -> str:
    try:
        h2 = driver.find_element(By.CLASS_NAME, "youraccount_pageheader")
        return h2.text.replace("'s Account", "").strip()
    except Exception:
        return "Неизвестно"

def extract_family_members(driver) -> list[str]:
    members = []
    try:
        elements = driver.find_elements(By.CLASS_NAME, "nOdcT-MoOaXGePXLyPe0H")
        for el in elements:
            text = el.text.strip()
            if text:
                members.append(text)
    except Exception:
        pass
    return members


async def parse_family_members(session_id: str, steam_login_secure: str) -> tuple[str, io.BytesIO | None]:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    byte_io = None
    try:
        driver.get("https://steampowered.com")
        time.sleep(1)
        driver.delete_all_cookies()
        driver.add_cookie({"name": "sessionid", "value": session_id, "domain": ".steampowered.com"})
        driver.add_cookie({"name": "steamLoginSecure", "value": steam_login_secure, "domain": ".steampowered.com"})

        driver.get("https://store.steampowered.com/account/familymanagement?tab=manage")
        time.sleep(5)
        members = extract_family_members(driver)

        driver.get("https://store.steampowered.com/account/familymanagement?tab=history")
        time.sleep(5)
        screenshot = driver.get_screenshot_as_png()
        img = Image.open(io.BytesIO(screenshot))
        width, height = img.size
        cropped_img = img.crop((705, 320, width - 500, height - 100))
        byte_io = io.BytesIO()
        cropped_img.save(byte_io, format="PNG")
        byte_io.seek(0)

        if not members:
            return "Данных нет. Скриншот истории сохранён.", byte_io
        return f"Найдено {len(members)} участников:\n" + "\n".join(f"👤 {m}" for m in members), byte_io

    except Exception as e:
        return f"Ошибка при получении данных: {e}", None
    finally:
        driver.quit()

conn = sqlite3.connect("steam_accounts.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    nickname TEXT,
    session_id TEXT,
    steam_login_secure TEXT
)
""")
conn.commit()
conn.close()

