import json
import os
from settings import USERS_FILE
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from bot_instance import bot
from telebot import types
from parsing import getTextSelectora
import threading
import re
import websocket
from uuid import uuid4
from APItest import getInfoUser
# =========================================================
# РАБОТА С ПОЛЬЗОВАТЕЛЯМИ (users.json)
# =========================================================
def add_plugins(user_id, value):
    '''Добавляет инфо о плагинах'''
    with open("users.json", "r", encoding="utf-8") as f:
        users = json.load(f)

    users[str(user_id)]["plugins"] = value

    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


# add_plugins("7378924678", ['Chat'])


def get_plugins(user_id):
    '''Ищет по id плагины у человека'''
    with open("users.json", "r", encoding="utf-8") as f:
        users = json.load(f)

    user_id = str(user_id)

    if user_id not in users:
        return None  

    return users[user_id].get("plugins", [])




def save_user(message):
    """Создаёт/обновляет запись пользователя в users.json (пустой nbgr)."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                users = {}
    else:
        users = {}

    user_id = str(message.chat.id)
    users[user_id] = {
        "id": user_id,
        "nbgr": "",
    }

    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


def set_nbgr(user_id, value):
    """Записывает NBGR-токен для пользователя."""
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)

    users[str(user_id)]["nbgr"] = value

    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


def nbgr(message):
    """Возвращает заголовки запроса (cookie) с NBGR-токеном пользователя."""
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)

    user_id = str(message.chat.id)
    nbgr_token = users[user_id]["nbgr"]

    headers = {
        "cookie": f"NBGR={nbgr_token}",
    }
    return headers




# ========================================================= 
# Функции
# =========================================================






user_threads = {}
threads_lock = threading.Lock()


def ensure_user_thread_started(user_id):
    with threads_lock:
        thread = user_threads.get(user_id)

        if thread and thread.is_alive():
            return False  # поток уже есть

        thread = threading.Thread(
            target=newmessage,
            args=(user_id,),
            daemon=True
        )
        user_threads[user_id] = thread
        thread.start()
        return True














def send_welcome(message):
    try:
        headers = nbgr(message)
        txt = getTextSelectora(headers)

        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="Профиль", callback_data="btn1")
        

        btn2 = types.InlineKeyboardButton(text="Плагины", callback_data="plugin")
        markup.add(btn1, btn2)

        ensure_user_thread_started(message.chat.id)

        bot.send_message(message.chat.id, txt, reply_markup=markup, parse_mode="html")

    except Exception:
        start_login(message)






def send_message(message, text, url):
    headers = nbgr(message)
    ws_url = "wss://petachok.ru:443/Services/ChatHandler.ashx"
   
    tousname, tousid, myname, myid = getInfoUser(headers, url)

    guid = str(uuid4())
    
    
    ws = websocket.create_connection(ws_url, header=headers, timeout=5)
    
   

    
    ws.send(f"{myname}{{#}}{guid}{{#}}openwebsoketforuser")
    
    ws.send(f"{myname}{{#}}{guid}{{#}}sendmessage{{%}}{myname}{{%}}{tousname}{{%}}{text}{{%}}{myid}{{%}}{tousid}{{%}}")
    
    ws.send(f"{myname}{{#}}{guid}{{#}}closwebsoketforuser")
    
    
    ws.close()










def get_headers_by_user_id(user_id):
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)

    nbgr_token = users[str(user_id)]["nbgr"]

    return {
        "cookie": f"NBGR={nbgr_token}"
    }

reply_storage = []
def newmessage(user_id):
    while True:
        try:
            headers = get_headers_by_user_id(user_id)

            text = requests.get(
                "https://petachok.ru/home/message",
                headers=headers,
                timeout=5
            ).text

            if "Новое сообщение" in text:
                result = getmessageinfo(text, headers)

                if result is not None:
                    mes, full_url = result
                    text = mes
                    lines = text.strip().split("\n", 1)
                    reply_storage.append(full_url)
                    name = lines[0].split()[0]      # первое слово первой строки — это имя
                    message_text = lines[1] if len(lines) > 1 else ""

                    markup = types.InlineKeyboardMarkup()
                    btn1 = types.InlineKeyboardButton(text="Ок", callback_data="delmes")
                    btn2 = types.InlineKeyboardButton(text="Ответить", callback_data="otvet")
                    markup.add(btn1, btn2)

                    txt = f'''

💬 <b>Новое сообщение</b>
От: <b>{name}</b>

<blockquote>{message_text}</blockquote>



'''
                    bot.send_message(user_id, txt, reply_markup=markup, parse_mode='html')
                    print(f"Новое сообщение у пользователя {user_id}: От {name}: {message_text}, ")
                    
                else:
                    print(f"У пользователя {user_id} есть отметка о новом сообщении, но текст не удалось получить")

        except Exception as e:
            pass

        time.sleep(3)





def getmessageinfo(text, headers):
    soup = BeautifulSoup(text, 'html.parser')


    message_element = soup.find(string=lambda text: text and "Новое сообщение" in text)

    if message_element:
       
        parent_link = message_element.find_parent('a')
        
        if parent_link and parent_link.has_attr('href'):
            relative_href = parent_link['href']
            
            
            base_url = "https://petachok.ru"  
            full_url = urljoin(base_url, relative_href)
            
            time.sleep(1.5)
            html_content = requests.get(full_url, headers=headers)
            
            soup = BeautifulSoup(html_content.text, 'html.parser')

            # Находим ВСЕ элементы с классом .messmyclass внутри .chat-mesacy
            messages = soup.select("div.chat-mesacy div.messmyclass")

            if messages:
                # Берем самый последний (нижний) элемент из списка
                last_message = messages[-1]
                
                # Выводим его чистый текст
                mes = last_message.text.strip()
            
            
                return mes, full_url


def gettoken(payload):
    url = "https://petachok.ru/userlogin"

   

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
    return token









def start_login(message):
    save_user(message)
    bot.send_photo(
    message.chat.id,
    photo=open("logininfo.jpg", "rb"),
    caption="Для начала работы войдите в аккаунт petachok.ru \n\nВведите логин:",
    parse_mode="html",
)

    bot.register_next_step_handler(message, get_login)


def get_login(message):
    chat_id = message.chat.id
    login = message.text.strip()

    bot.send_photo(
        message.chat.id,
        photo=open("password.png", "rb"),
        caption="Теперь нужен пароль, если вы его не знаете, то инструкция для его получения выше ☝️\nСначала вы копируете почту из меню Безопасность и выходите с аккаунта,\nпотом заходите в меню входа, и жмете Забыли пароль,\nзатем на почту приходит первое письмо, в нем жмете Перейти\nи приходит второе письмо как на третем скрине\n\nВведите пароль: ",
        parse_mode="html",
    )

    bot.register_next_step_handler(message, get_password , login)

def get_password(message, login):
    password = message.text.strip()
    payload = {
            "User": f"{login}",
            "Pass": f"{password}"
        }
    
    token = gettoken(payload)
    if token != None:
        set_nbgr(message.chat.id, token)

        bot.send_message(message.chat.id, 'Вход в аккаунт успешно выполнен!\nОтправьте /start для начала работы!')
    else:

        bot.send_message(message.chat.id, 'Логин или пароль не правильны!\nПопробуйте снова /start')