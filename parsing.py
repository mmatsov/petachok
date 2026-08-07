import requests
from bs4 import BeautifulSoup
from settings import BASE_URL, SELECTOR_MAIN_BALANCE, SELECTOR_HOLD, SELECTOR_USER_NAME
import re
# =========================================================
# ПАРСИНГ САЙТА
# =========================================================
def get_deals_stats(headers, url):
    html_content = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html_content, "html.parser")

    container = soup.select_one("body > div.main-content > div > div > div.mainBlock > div.hr")
    if container is None:
        return {"active_count": 0, "active_sum": 0, "total_count": 0, "total_sum": 0}

    deals = container.select("a.buttonMainBlock")

    active_count = 0
    active_sum = 0
    total_count = 0
    total_sum = 0

    for deal in deals:
        # статус сделки (например "Активна")
        status_el = deal.select_one("span.c-green, span.c-red, span.c-orange")
        status = status_el.get_text(strip=True) if status_el else ""

        # сумма сделки — ищем блок с текстом "Сумма сделки:"
        sum_text = None
        for div in deal.select("div"):
            text = div.get_text(strip=True)
            if text.startswith("Сумма сделки:"):
                sum_text = div
                break

        amount = 0
        if sum_text:
            bold = sum_text.select_one("b")
            if bold:
                # убираем всё, кроме цифр
                digits = re.sub(r"[^\d]", "", bold.get_text(strip=True))
                amount = int(digits) if digits else 0

        total_count += 1
        total_sum += amount

        if status == "Активна":
            active_count += 1
            active_sum += amount

    return {
        "active_count": active_count,
        "active_sum": active_sum,
        "total_count": total_count,
        "total_sum": total_sum,
    }

def getTextSelectora(headers):
    """Забирает главную страницу и возвращает текст приветствия с балансом."""
    html_content = requests.get(BASE_URL, headers=headers).text
    soup = BeautifulSoup(html_content, "html.parser")

    element = soup.select_one(SELECTOR_MAIN_BALANCE)
    element2 = soup.select_one(SELECTOR_HOLD)
    element3 = soup.select_one(SELECTOR_USER_NAME)
    stats = get_deals_stats(headers, 'https://petachok.ru/home/mydeals')
    if element:
        
        text_content = f"""
👋 <b>Добрый день, {element3.get_text(strip=True)}!</b>
──────────────────
💰 Баланс: <code>{element.get_text(strip=True)}</code>
⏳ В холде: <code>{element2.get_text(strip=True)}</code>

📊 <b>Статистика сделок:</b>
    ├ Активных сделок: <code>{stats['active_count']}</code>
    └ Сумма в сделках: <code>{stats['active_sum']}</code>
    """
        return text_content
    else:
        print("Элемент не найден. Проверьте правильность селектора.")


def getTextSelectora2(headers, selector, url):
    """Универсальный парсер: забирает url и возвращает текст по CSS-селектору."""
    html_content = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html_content, "html.parser")
    element = soup.select_one(selector)
    text = element.get_text(strip=True)
    return text


def getLinkSelectora1(headers, url, selector):
    """Находит внутри selector тег <a> и возвращает его href."""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        element = soup.select_one(selector)

        if element:
            link_tag = element.find("a")
            if link_tag:
                href = link_tag.get("href")
                if href:
                    return href
                else:
                    print(f"⚠️ Тег <a> найден внутри '{selector}', но у него нет атрибута href.")
                    return None
            else:
                print(f"⚠️ Внутри селектора '{selector}' не найден тег <a>.")
                return None
        else:
            print(f"⚠️ Элемент по селектору '{selector}' не найден на странице.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при запросе к сайту: {e}")
        return None




