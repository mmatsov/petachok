import telebot

# =========================================================
# НАСТРОЙКИ
# =========================================================



USERS_FILE = "users.json"
BASE_URL = "https://petachok.ru/getmoney"

# Селекторы для главной страницы (баланс/холд/имя)
SELECTOR_MAIN_BALANCE = (
    "body > div.main-content > div > div > div:nth-child(3) > "
    "div > div:nth-child(1) > div > div.size-60_.bold"
)
SELECTOR_HOLD = (
    "body > div.main-content > div > div > div:nth-child(3) > "
    "div > div:nth-child(2) > div > div.size-60_.bold"
)
SELECTOR_USER_NAME = (
    "#userMenu > div > a.padding-10_.innerBlock > "
    "div.flexColumn.gap-5.ai-center > div"
)
SELECTOR_PROFILE_LINK = "#userMenu > div"

# Селекторы для страницы рейтинга/отзывов
SELECTOR_RATING = (
    "body > div.main-content > div.width-900_ > div > div:nth-child(4) > "
    "div > div.flexColumn.gap-10 > div:nth-child(1) > div > div > div.size-60_"
)
SELECTOR_GREEN = (
    "body > div.main-content > div.width-900_ > div > div:nth-child(4) > "
    "div > div.flexColumn.gap-10 > div:nth-child(2) > div > div.c-green > div.size-40_"
)
SELECTOR_YELLOW = (
    "body > div.main-content > div.width-900_ > div > div:nth-child(4) > "
    "div > div.flexColumn.gap-10 > div:nth-child(2) > div > div.c-orange > div.size-40_"
)
SELECTOR_RED = (
    "body > div.main-content > div.width-900_ > div > div:nth-child(4) > "
    "div > div.flexColumn.gap-10 > div:nth-child(2) > div > div.c-red > div.size-40_"
)
