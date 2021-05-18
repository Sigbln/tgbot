import schedule
import telebot
import threading
import time

from datetime import date
from telebot import types

import config
import db
import menu
import messages

bot = telebot.TeleBot(config.token)

resp = None

db = db.DataBase()


def gen_menu(bots, message, way, button):
    ''' Принимает в себя бота, полученное сообщение, путь куда потом пойти,
        и какую кнопку сделать '''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    itembtn1 = types.KeyboardButton(button)
    markup.add(itembtn1)
    msg = bots.send_message(message.chat.id,
                            messages.ans_1,
                            reply_markup=markup)
    bots.register_next_step_handler(msg, way)


@bot.message_handler(commands=['start', 'help'])
def step_one(message):
    '''С команды start/help спрашивает чего хочет пользователь'''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    itembtn1 = types.KeyboardButton(menu.menu[0])
    itembtn2 = types.KeyboardButton(menu.menu[1])
    markup.add(itembtn1, itembtn2)
    msg = bot.send_message(message.chat.id,
                           messages.menu_message,
                           reply_markup=markup)
    bot.register_next_step_handler(msg, step_two)


def step_two(message):
    '''Проверяет что выбрал пользователь и выбирает нужный путь'''
    global resp
    markup = types.ReplyKeyboardRemove(selective=False)

    if message.text == menu.menu[0]:
        temp_date = date.today()
        resp = db.get_rates(str(temp_date))
        gen_menu(bot, message, way_1, menu.btn_all)
        pass

    elif message.text == menu.menu[1]:
        msg = bot.send_message(message.chat.id,
                               messages.ans_2,
                               reply_markup=markup)
        bot.register_next_step_handler(msg, way_2)
    else:
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, messages.error,
                         reply_markup=markup,
                         parse_mode="Markdown")
        pass


def way_1(message):
    '''Спрашивает пользователя какую валюту он хочет узнать'''
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id,
                     messages.mess_gen(resp, coin=message.text),
                     reply_markup=markup,
                     parse_mode="Markdown")
    pass


def way_2(message):
    '''Спрашивает за какую дату он хочет узнать и направляет в way_1'''
    global resp
    types.ReplyKeyboardRemove(selective=False)
    temp_date = message.text.split('.')
    temp_date = date(temp_date[2], temp_date[1], temp_date[0])
    resp = db.get_rates(str(temp_date))
    gen_menu(bot, message, way_1, menu.btn_all)
    pass


@bot.message_handler(commands=['sub'])
def subscribe(message):
    msg = db.add_sub(str(message.from_user.id))
    bot.send_message(message.chat.id, msg)
    pass


@bot.message_handler(commands=['unsub'])
def unsubscribe(message):
    msg = db.unsub(str(message.from_user.id))
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['sndmsgall'])
def mess(message):
    resp = db.update_data()
    subs = db.get_subs()
    for user in subs:
        bot.send_message(user[1], messages.mess_gen(resp),
                         parse_mode="Markdown")


def run_threaded(func):
    job_thread = threading.Thread(target=func)
    job_thread.start()


def mailing():
    markup = types.ReplyKeyboardRemove(selective=False)
    temp_date = date.today()
    resp = db.get_rates(str(temp_date))
    for user in db.get_subs():
        bot.send_message(user, messages.mess_gen(resp),
                         reply_markup=markup,
                         parse_mode="Markdown")


bot_thread = threading.Thread(target=bot.polling)
bot_thread.start()
schedule.every().day.at("09:00").do(run_threaded, mailing)


def main_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main_loop()
