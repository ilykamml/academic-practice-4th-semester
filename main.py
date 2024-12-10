import telebot, feedparser, time
from telebot.types import Message
from threading import Thread
from user_class import *
from rss_class import *

with open('TOKEN', 'r') as file:
    TOKEN = file.read().strip()

with open('ADMINID', 'r') as file:
    ADMINID = int(file.read().strip())

bot = telebot.TeleBot(TOKEN)

users = UserManager()
links = RSSManager()

@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    bot.reply_to(message, 'Привет, для начала отправь мне RSS ссылку на интересующий тебя ресурс!')

@bot.message_handler(func=lambda message: True)
def add_rss_feed(message: Message):
    id, username, url = message.from_user.id, message.from_user.username, message.text
    # добавляем пользователя в список (если пользователь есть - данные не перезапишутся)
    users.add_user(id, username)
    # добавляем rss-канал в список (если канал есть - данные не перезапишутся)
    links.add_source(url.strip())
    users.get_user(id).add_sub(links.get_source(url))
    bot.send_message(ADMINID, f'USERS:\n{users}\n\n\nCHANNELS:\n{links}') # DEBUG



if __name__ == '__main__':
    while True:
        try:
            bot.polling(timeout=30, long_polling_timeout=30)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(15) # ждём перед следующей попыткой