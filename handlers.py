from telebot import types
from bot_instance import bot
from func import save_user, set_nbgr, nbgr, newmessage, ensure_user_thread_started, send_welcome
from parsing import getTextSelectora
import threading

# =========================================================
# ОБРАБОТЧИКИ КОМАНД
# =========================================================




@bot.message_handler(commands=["start"])
def awge(message):
    
    send_welcome(message)

@bot.message_handler(commands=["nbgr"])
def add_nbgr_token(message):
    save_user(message)
    set_nbgr(message.chat.id, message.text[6:])
    bot.send_message(
        message.chat.id,
        "Токен добавлен!\nОтправьте /start",
        parse_mode="html"
    )


