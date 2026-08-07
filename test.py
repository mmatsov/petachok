import requests
def gettoken(payload):
    url = "https://petachok.ru/userlogin"

    payload = {
        "User": "g376660",
        "Pass": "Aa570866"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        # при необходимости добавь User-Agent, Referer и т.п., 
        # если сайт проверяет их (иначе может вернуть ошибку/редирект)
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://petachok.ru/",
    }

    session = requests.Session()

    resp = session.post(url, data=payload, headers=headers)




    # Достаём конкретно нужную куку
    token = resp.cookies.get("NBGR")
    if token:
        print("NBGR token:", token)
    else:
        print("Кука NBGR не найдена в ответе. Проверь Set-Cookie заголовки:")
        print(resp.headers.get("Set-Cookie"))