import requests
import telebot
from telebot import types

import config
import db
import menu as mn
import messages as ms

bot = telebot.TeleBot(config.token)

resp = None

db = db.SQLighter('identifier.sqlite')


def gen_menu(bots, message, way, button):
    ''' Принимает в себя бота, полученное сообщение, путь куда потом пойти,
        и какую кнопку сделать '''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    itembtn1 = types.KeyboardButton(button)
    markup.add(itembtn1)
    msg = bots.send_message(message.chat.id,
                            ms.ans_1,
                            reply_markup=markup)
    bots.register_next_step_handler(msg, way)
    return markup


@bot.message_handler(commands=['start', 'help'])
def step_one(message):
    '''С команды start/help спрашивает чего хочет пользователь'''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    itembtn1 = types.KeyboardButton(mn.menu[0])
    itembtn2 = types.KeyboardButton(mn.menu[1])
    markup.add(itembtn1, itembtn2)
    msg = bot.send_message(message.chat.id,
                           ms.menu_message,
                           reply_markup=markup)
    bot.register_next_step_handler(msg, step_two)


def step_two(message):
    '''Проверяет что выбрал пользователь и выбирает нужный путь'''
    global resp
    markup = types.ReplyKeyboardRemove(selective=False)

    if message.text == mn.menu[0]:
        resp = requests.get(config.url_latest).json()
        markup = gen_menu(bot, message, way_1, mn.btn_all)
        pass

    elif message.text == mn.menu[1]:
        msg = bot.send_message(message.chat.id,
                               ms.ans_2,
                               reply_markup=markup)
        bot.register_next_step_handler(msg, way_2)
    else:
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, ms.error,
                         reply_markup=markup,
                         parse_mode="Markdown")
        pass


def way_1(message):
    '''Спрашивает пользователя какую валюту он хочет узнать'''
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, ms.mess_gen(resp, coin=message.text),
                     reply_markup=markup,
                     parse_mode="Markdown")
    pass


def way_2(message):
    '''Спрашивает за какую дату он хочет узнать и направляет в way_1'''
    global resp
    markup = types.ReplyKeyboardRemove(selective=False)
    date = message.text.split('.')
    date = f'{date[2]}-{date[1]}-{date[0]}'
    resp = requests.get(
        config.url_date_first + date + config.url_date_last).json()
    markup = gen_menu(bot, message, way_1, mn.btn_all)
    pass


@bot.message_handler(commands=['sub'])
def subscribe(message):
    if (not db.subscriber_exists(message.from_user.id)):
        # если юзера нет в базе, добавляем его
        db.add_subscriber(message.from_user.id)
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        db.update_subscription(message.from_user.id, True)
    bot.send_message(message.chat.id, ms.sub)
    pass


@bot.message_handler(commands=['unsub'])
def unsubscribe(message):
    if (not db.subscriber_exists(message.from_user.id)):
        # если юзера нет в базе, добавляем его с неактивной подпиской
        db.add_subscriber(message.from_user.id, False)
        bot.send_message(message.chat.id, ms.unsub_1)
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        db.update_subscription(message.from_user.id, False)
        bot.send_message(message.chat.id, ms.unsub_2)


@bot.message_handler(commands=['sndmsgall'])
def mess(message):
    resp = requests.get(config.url_latest).json()
    subs = db.get_subscriptions()
    for user in subs:
        bot.send_message(user[1], ms.mess_gen(resp), parse_mode="Markdown")


if __name__ == '__main__':
    bot.polling(none_stop=True)
