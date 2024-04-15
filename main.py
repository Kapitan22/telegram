import telebot
from telebot import types
from bs4 import BeautifulSoup
import requests
import datetime
import sqlite3
import time


url_weather = 'https://yandex.by/pogoda/brest'
# 52.368636
# 23.372988

token = '6758162867:AAFIfr2bpOE0ZbO_pYb2Vb-zrYxnH3i4IbE'
bot = telebot.TeleBot(token)

name = None
password = None
ip = None
USER = 0
user_log = 0

admin = ["maxim", "m1234"]


@bot.message_handler(commands=['start'])
def start(message):
    global name, password, ip, USER
    name = None
    password = None
    ip = None
    USER = 0
    conn = sqlite3.connect('bd_telegram.sql')
    cur = conn.cursor()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50), ip varchar(50))')
    conn.commit()
    cur.close()
    conn.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Главное меню")
    btn2 = types.KeyboardButton("Что я могу?")
    markup.add(btn1, btn2)

    bot.send_message(message.chat.id, text="Добро пожаловать в Умный дом!!!", reply_markup=markup)
    bot.send_message(message.chat.id, 'Зарегестрируйтесь пожалуйста /login')
    bot.send_message(message.chat.id, 'Если у вас есть аккаут в боте то войдите /sign')


@bot.message_handler(commands=['sign'])
def input_name_password(message):
    global user_log, USER
    user_log = 1
    bot.send_message(message.chat.id, 'write name and password')
    bot.register_next_step_handler(message, sign)


def sign(message):
    global name, password, ip, USER
    s = str(message.text)
    name = s[:s.find(' ')]
    password = s[s.find(' ') + 1:]
    print(name)
    print(password)
    conn = sqlite3.connect('bd_telegram.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    for user in users:
        if user[1] == name and user[2] == password:
            USER = 1
            ip = user[3]
            USER = 1
            print(*user)

    if USER == 0:
        bot.send_message(message.chat.id, 'Неверное имя пользователя или пороль')
    else:
        bot.send_message(message.chat.id, 'Вы вошли в аккаутн')
        bot.send_message(message.chat.id, '/out')

    cur.close()
    conn.close()


@bot.message_handler(commands=['out'])
def out(message):
    global USER
    USER = 0
    bot.send_message(message.chat.id, 'Вы вышли из аккаунта')


@bot.message_handler(commands=['list'])
def list_users(message):
    conn = sqlite3.connect('bd_telegram.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    info = ''

    for i in users:
        info += f'Name: {i[1]}, password: {i[2]}, ip: {i[3]}\n'

    cur.close()
    conn.close()

    bot.send_message(message.chat.id, info)


@bot.message_handler(commands=['login'])
def input_name_password_ip(message):
    global user_log, USER
    user_log = 1
    bot.send_message(message.chat.id, 'write name password and ip')
    bot.register_next_step_handler(message, login)


def login(message):
    global name, password, ip, USER
    s = str(message.text)
    name = s[:s.find(' '):]
    s1 = s[s.find(' ') + 1:]
    password = s1[:s1.find(' ') + 1]
    ip = s1[s.find(' ') + 1:]

    conn = sqlite3.connect('bd_telegram.sql')
    cur = conn.cursor()

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    n = False

    for user in users:
        if user[1] == name and user[2] == password:
            n = True
            print('------------')

    if n:
        bot.send_message(message.chat.id, "Такой пользоватьль уже существует, попробуйте ещё раз /login")
    else:
        cur.execute(
            "INSERT INTO users (name, pass, ip) VALUES ('%s', '%s', '%s')" % (name, password, ip))
        conn.commit()
        USER = 1
        bot.send_message(message.chat.id, 'Вы вошли в аккаутн')
        bot.send_message(message.chat.id, '/out')
    cur.close()
    conn.close()


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    conn = sqlite3.connect('bd_telegram.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    info = ''

    for i in users:
        info += f'Name: {i[1]}, password: {i[2]}, ip: {i[3]}\n'

    cur.close()
    conn.close()


@bot.message_handler(commands=['clr_users'])
def clr(message):
    conn = sqlite3.connect('bd_telegram.sql')
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM users;")
    conn.commit()

    cur.close()
    conn.close()


def button_ihome(*args, **kwargs) -> list:
    b_on = types.KeyboardButton('Включить свет')
    b_of = types.KeyboardButton('Выключить свет')
    b_t = types.KeyboardButton("Tемпература в доме")
    b_w = types.KeyboardButton("Затопление")
    b_g = types.KeyboardButton("Oсвещение")
    auth = types.KeyboardButton("Кто дома")
    back = types.KeyboardButton("Главное меню")
    return [[b_on, b_of], [b_t, b_w, b_g], [back], [auth]]


def get_weather():
    res = requests.get(url_weather)
    bs = BeautifulSoup(res.text, "lxml")
    return bs.find("span", class_="temp__value temp__value_with-unit")


def get_data():
    return "Год - {}\nМесяц - {}\nДень - {}\nДата - {}:{}".format(
        datetime.datetime.now().year,
        datetime.datetime.now().month,
        datetime.datetime.now().day,
        datetime.datetime.now().hour,
        datetime.datetime.now().minute
    )


def get_temperature() -> str:
    try:
        url = "http://" + str(ip) + "/temperature"
        r = requests.get(url)
    except:
        return "not found ip: '%s'" % ip
    else:
        return r.text


def get_light() -> str:
    try:
        url = "http://" + str(ip) + "/light"
        r = requests.get(url)
    except:
        return "not found ip: '%s'" % ip
    else:
        return r.text


def get_water() -> str:
    try:
        url = "http://" + str(ip) + "/water"
        r = requests.get(url)
    except:
        return "not found ip: '%s'" % ip
    else:
        return r.text


def get_ledOn() -> str:
    try:
        url = "http://" + str(ip) + "/ledOn"
        r = requests.get(url)
    except:
        return "not found ip: '%s'" % ip
    else:
        return r.text


def get_ledOff() -> str:
    try:
        url = "http://" + str(ip) + "/ledOff"
        r = requests.get(url)
    except:
        return "not found ip: '%s'" % ip
    else:
        return r.text


@bot.message_handler(content_types=["text"])
def main(message):
    if USER == 1:
        if message.text == "Главное меню":
            b_w = types.InlineKeyboardButton('Погода')
            b_v = types.InlineKeyboardButton('Дата')
            b_y = types.InlineKeyboardButton("Умный дом")

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(b_w)
            markup.add(b_v)
            markup.add(b_y)
            # markup.add(b_h)
            bot.send_message(message.chat.id, text="Главное меню", reply_markup=markup)

        elif message.text == "Что я могу?":
            bot.send_message(message.chat.id, text="1 Погода - выводит погоду в настоящее веремя\n"
                                                   "2 Дата - выводит погоду в настоящее веремя\n"
                                                   "3 Умный дом - выводит погоду в настоящее веремя\n"
                                                   "- Температура в доме\n"
                                                   "- Влажность воздуха\n"
                                                   "- Освещение")
        elif message.text == "Погода":
            a = get_weather()
            bot.send_message(message.chat.id, text=a)

            bot.send_message(message.chat.id, text="Погода")
        elif message.text == "Дата":
            n = get_data()
            bot.send_message(message.chat.id, text=n)
        elif message.text == "Умный дом":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            sp = button_ihome()
            for i in sp:
                markup.row(*i)
            bot.send_message(message.chat.id, text="Умный дом", reply_markup=markup)
        elif message.text == "Tемпература в доме":
            tp = get_temperature()
            bot.send_message(message.chat.id, text=tp)

        elif message.text == "Затопление":
            w = get_water()
            bot.send_message(message.chat.id, text=w)

        elif message.text == "Oсвещение":
            l = get_light()
            bot.send_message(message.chat.id, text=l)
        elif message.text == "Включить свет":
            get_ledOn()
        elif message.text == "Выключить свет":
            get_ledOff()
    else:
        bot.send_message(message.chat.id, 'Вы не вошли в аккаунт')


bot.infinity_polling()
