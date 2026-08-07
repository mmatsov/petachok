from telebot import types
import logging
logging.basicConfig(level=logging.INFO, filename="bot.log", format="%(asctime)s %(levelname)s %(message)s")
from bot_instance import bot
from func import nbgr, get_plugins, reply_storage, send_message
from parsing import getTextSelectora, getLinkSelectora1, getTextSelectora2
from settings import (
    BASE_URL,
    SELECTOR_PROFILE_LINK,
    SELECTOR_RATING,
    SELECTOR_GREEN,
    SELECTOR_YELLOW,
    SELECTOR_RED,
)


def build_main_menu():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Профиль", callback_data="btn1")
    btn2 = types.InlineKeyboardButton(text="Плагины", callback_data="plugin")
    markup.add(btn1, btn2)
    return markup


@bot.callback_query_handler(func=lambda call: call.data == "main")
def show_main_menu(call):
    try:
        headers = nbgr(call.message)
        txt = getTextSelectora(headers)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=txt,
            reply_markup=build_main_menu(),
            parse_mode="html",
        )
    except Exception as e:
        print(f"Ошибка callback main: {e}")
        bot.answer_callback_query(call.id, "Ошибка открытия меню")


@bot.callback_query_handler(func=lambda call: call.data == "btn1")
def show_rating(call):
    try:
        headers = nbgr(call.message)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Загрузка...",
        )

        link = getLinkSelectora1(headers, BASE_URL, SELECTOR_PROFILE_LINK)
        reviews_url = f"https://petachok.ru/{link}#reviews"

        rating_value = getTextSelectora2(headers, SELECTOR_RATING, reviews_url)
        green = getTextSelectora2(headers, SELECTOR_GREEN, reviews_url)
        yellow = getTextSelectora2(headers, SELECTOR_YELLOW, reviews_url)
        red = getTextSelectora2(headers, SELECTOR_RED, reviews_url)

        total_reviews = int(green) + int(yellow) + int(red)
        text = (
            f"📈 <b>Рейтинг:</b> <code>{rating_value} ★</code>\n\n"
            f"<b>Статистика отзывов ({total_reviews}):</b>\n"
            f"└ 🟢 <b>{green}</b> │ 🟡 <b>{yellow}</b> │ 🔴 <b>{red}</b>"
        )

        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="Главное меню", callback_data="main")
        markup.add(btn1)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup,
            parse_mode="html",
        )
    except Exception as e:
        print(f"Ошибка callback btn1: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки профиля")


@bot.callback_query_handler(func=lambda call: call.data == "delmes")
def delete_notification(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(f"Ошибка callback delmes: {e}")
        bot.answer_callback_query(call.id, "Не удалось удалить сообщение")


@bot.callback_query_handler(func=lambda call: call.data == "plugin")
def show_plugins(call):
    try:
        plugins = get_plugins(call.message.chat.id)

        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="Главное меню", callback_data="main")
        markup.add(btn1)

        if plugins:
            text = f"Ваши плагины:\n{plugins}"
        else:
            text = "У вас нет плагинов\nО плагинах:"

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup,
        )
    except Exception as e:
        print(f"Ошибка callback plugin: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки плагинов")



@bot.callback_query_handler(func=lambda call: call.data == "nepisat")
def cancel_message(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)  



@bot.callback_query_handler(func=lambda call: call.data == "otvet")
def show_rating(call):
    mesid = call.message.message_id
    mestext = call.message.text
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Отмена", callback_data="nepisat")
    markup.add(btn1)

    prompt = bot.send_message(
        chat_id=call.message.chat.id,
        text='Введите сообщение:',
        reply_markup=markup,
    )
    prompt_id = prompt.message_id 

    bot.register_next_step_handler(call.message, send, mesid, mestext, prompt_id)


def send(message, mesid, mestext, prompt_id):
    chat_id = message.chat.id
    text = message.text

    try:
        url = reply_storage[0]
    except (IndexError, KeyError) as e:
        logging.error(f"reply_storage error: {e}")
        bot.send_message(chat_id, "⚠️ Ошибка. Попробуйте начать заново.")
        return

    if not url or not text:
        logging.error(f"Пустой url или text: url={url}, text={text}")
        bot.send_message(chat_id, "⚠️ Ошибка. Попробуйте начать заново.")
        return

    try:
        send_message(message, text, url)
    except Exception as e:
        logging.error(f"Ошибка send_message: {e}")
        bot.send_message(chat_id, "⚠️ Не удалось отправить сообщение. Попробуйте позже.")
        return  # НЕ идём дальше — раз отправка не удалась, не трогаем UI

    # Только если отправка реально прошла успешно — чистим UI
    try:
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
    except Exception as e:
        logging.warning(f"Не удалось удалить сообщение юзера: {e}")

    try:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="Ок", callback_data="delmes")
        markup.add(btn1)

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=prompt_id,
            text='✅ Отправлено',
            reply_markup=markup,
            parse_mode="html",
        )
    except Exception as e:
        logging.warning(f"Не удалось отредактировать сообщение: {e}")
        # НЕ отправляем новое сообщение "на всякий случай" —
        # раз ошибка непредвиденная, лучше просто залогировать,
        # чтобы не продублировать/не запутать пользователя