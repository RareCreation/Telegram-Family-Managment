from aiogram.fsm.state import StatesGroup, State

class UploadCookiesStates(StatesGroup):
    waiting_for_session_id = State()
    waiting_for_steam_login_secure = State()
