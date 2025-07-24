import sqlite3

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, BufferedInputFile

from states.states import UploadCookiesStates
from utils.selenium.run_util import run_selenium_check, parse_family_members

router = Router()

@router.message(Command("start"))
async def handle_start(message: Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Список аккаунтов", callback_data="list_accounts"),
            InlineKeyboardButton(text="Загрузить аккаунт", callback_data="upload_account")
        ],
        [
            InlineKeyboardButton(text="Выгрузить аккаунт", callback_data="delete_account_list")
        ]
    ])

    await message.answer("Выберите одну из функций", reply_markup=keyboard)

@router.callback_query(F.data == "list_accounts")
async def handle_account_list(c: CallbackQuery):
    conn = sqlite3.connect("steam_accounts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nickname FROM accounts WHERE user_id = ?", (c.from_user.id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await c.message.answer("У вас пока нет аккаунтов.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=row[0], callback_data=f"account_{row[0]}")] for row in rows
    ])
    await c.message.answer("Ваши аккаунты:", reply_markup=keyboard)


@router.callback_query(F.data == "upload_account")
async def handle_upload_account(c: CallbackQuery, state: FSMContext):
    await c.message.answer("Отправьте session_id:")
    await state.set_state(UploadCookiesStates.waiting_for_session_id)

@router.message(UploadCookiesStates.waiting_for_session_id)
async def process_session_id(message: Message, state: FSMContext):
    await state.update_data(session_id=message.text)
    await message.answer("Теперь отправьте steamLoginSecure:")
    await state.set_state(UploadCookiesStates.waiting_for_steam_login_secure)

@router.message(UploadCookiesStates.waiting_for_steam_login_secure)
async def process_steam_login_secure(message: Message, state: FSMContext):
    user_data = await state.get_data()
    session_id = user_data["session_id"]
    steam_login_secure = message.text

    nickname, result = await run_selenium_check(session_id, steam_login_secure)

    if nickname:
        conn = sqlite3.connect("steam_accounts.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO accounts (user_id, nickname, session_id, steam_login_secure) VALUES (?, ?, ?, ?)",
            (message.from_user.id, nickname, session_id, steam_login_secure)
        )
        conn.commit()
        conn.close()

    await message.answer(result)
    await state.clear()


@router.callback_query(F.data.startswith("account_"))
async def handle_account_info(c: CallbackQuery):
    nickname = c.data.split("account_")[1]
    conn = sqlite3.connect("steam_accounts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT session_id, steam_login_secure FROM accounts WHERE user_id = ? AND nickname = ?", (c.from_user.id, nickname))
    row = cursor.fetchone()
    conn.close()

    if not row:
        await c.message.answer("Аккаунт не найден.")
        return

    session_id, steam_login_secure = row
    result_text, screenshot_io = await parse_family_members(session_id, steam_login_secure)

    if screenshot_io is None:
        await c.message.answer(f"👨‍👩‍👧‍👦 <b>Аккаунт {nickname}</b>\n\n{result_text}\n\n⚠️ Не удалось получить скриншот", parse_mode="HTML")
    else:
        photo = BufferedInputFile(screenshot_io.read(), "screenshot.png")
        await c.message.answer_photo(photo=photo, caption=f"👨‍👩‍👧‍👦 <b>Аккаунт {nickname}</b>\n\n{result_text}", parse_mode="HTML")


@router.callback_query(F.data == "delete_account_list")
async def show_accounts_for_deletion(c: CallbackQuery):
    conn = sqlite3.connect("steam_accounts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nickname FROM accounts WHERE user_id = ?", (c.from_user.id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await c.message.answer("У вас пока нет аккаунтов для удаления.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=row[0], callback_data=f"delete_account_{row[0]}")] for row in rows
    ])
    await c.message.answer("Выберите аккаунт для удаления:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("delete_account_"))
async def delete_account_callback(c: CallbackQuery):
    nickname = c.data.split("delete_account_")[1]
    conn = sqlite3.connect("steam_accounts.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM accounts WHERE user_id = ? AND nickname = ?", (c.from_user.id, nickname))
    conn.commit()
    conn.close()

    await c.message.answer(f"Аккаунт {nickname} удалён.")

