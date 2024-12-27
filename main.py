import telebot, time
from telebot.types import Message
from threading import Thread
from user_class import *
from rss_class import *
from os.path import exists
import pickle
from threading import Event


with open('TOKEN', 'r') as file:
    TOKEN = file.read().strip()

with open('ADMINID', 'r') as file:
    ADMINID = int(file.read().strip())

stop_event = Event()
dont_stop_while = True

threads = []

bot = telebot.TeleBot(TOKEN)

if exists('data.pkl'):
    with open('data.pkl', 'rb') as data:
        data = pickle.load(data)
        users = data['users']
        links = data['links']
else:
    users = UserManager()
    links = RSSManager()

def shutdown_bot():
    global dont_stop_while
    dont_stop_while = False
    stop_threads()
    save_data('data.pkl')
    bot.stop_polling()
    bot.stop_bot()
    exit(0)

@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    users.add_user(message.from_user.id, message.from_user.username)
    bot.reply_to(message, 'Привет, для начала отправь мне RSS ссылку на интересующий тебя ресурс!')

@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message: Message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, f'Использование - /unsubscribe <url>')
    else:
        link = links.get_source(message.text.split(maxsplit=1)[1])
        if users.get_user(message.from_user.id).del_sub(link):
            if len(link.subscribers) == 0:
                links.remove_source(link.url)
            bot.reply_to(message, f'Теперь вы отписаны от этого потока')
        else: 
            print(message.text.split(maxsplit=1)[1])
            bot.reply_to(message, f'Кажется вы не подписаны на этот поток')
        save_data('data.pkl')

@bot.message_handler(commands=['myfeeds'])
def get_list(message: Message):
    result = 'Вот ваши подписки:\n'
    for i, sub in enumerate(users.get_user(message.from_user.id).subscribes):
        result += f'{i+1}. {sub.url}\n'
    bot.reply_to(message, result)

@bot.message_handler(commands=['feedback'])
def pull_feedback(message: Message):
    if len(message.text) < 10:
        bot.reply_to(message, f'Использование:\n/feedback <ваш отзыв>')
    else:
        feedback_text = message.text.split(maxsplit=1)[1]
        bot.reply_to(message, 'Спасибо за отзыв!')
        bot.send_message(ADMINID, f'Пришёл фидбэк от пользователя @{message.from_user.username}\n\n"{feedback_text}"')


@bot.message_handler(commands=['db', 'off'])
def debug_info(message: Message):
    if message.from_user.id == ADMINID:
        command = message.text.split(maxsplit=1)[0]
        if command == '/db':
            bot.reply_to(message, f'USERS:\n{users}\n\n\nCHANNELS:\n{links}')
        elif command == '/off':
            bot.reply_to(message, 'Выключение...')
            shutdown_bot()



@bot.message_handler(func=lambda message: True)
def add_rss_feed(message: Message):
    id, username, url = message.chat.id, message.from_user.username, message.text
    # добавляем пользователя в список (если пользователь есть - данные не перезапишутся)
    users.add_user(id, username)
    # добавляем rss-канал в список (если канал есть - данные не перезапишутся)
    links.add_source(url.strip())
    users.get_user(id).add_sub(links.get_source(url))
    bot.reply_to(message, 'RSS канал добавлен!\nСейчас подгрузим записи')

def check_feeds():
    while not stop_event.is_set():
        for source in links.get_sources():
            entries = source.fetch_entries()
            if entries:
                new_entries = source.filter_new_entries(entries)
                if new_entries:
                    for entry in new_entries:
                        title = entry.title
                        link = entry.link
                        # image = entry.media_content[0]['url'] if 'media_content' in entry else None
                        message_text = f"<b>{title}</b>\n<a href='{link}'>Читать далее</a>"
                        for user in source.subscribers:
                            # if image:
                            #     bot.send_photo(chat_id=user.id, photo=image, caption=message_text, parse_mode='HTML')
                            # else:
                            bot.send_message(chat_id=user.id, text=message_text, parse_mode='HTML')
                    save_data('data.pkl')

        time.sleep(30)

def save_data(file):
    with open(file, 'wb') as data:
        pickle.dump({'users': users, 'links': links}, data)

def stop_threads():
    stop_event.set()
    for thread in threads:
        thread.join

def start_threads():
    new_thread = Thread(target=check_feeds)
    new_thread.start()
    threads.append(new_thread)

if __name__ == '__main__':

    retry_delay = 15
    try:
        start_threads()
        retry_delay = 15
    except Exception as e:
        print(f'Error: {e}')
        stop_threads()
        time.sleep(retry_delay)
        retry_delay = min(retry_delay * 2, 960)
        start_threads()


    while dont_stop_while:
        try:
            bot.polling(timeout=30, long_polling_timeout=30)
            retry_delay = 15  # Reset delay after a successful polling
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(retry_delay)  # ждём перед следующей попыткой
            retry_delay = min(retry_delay * 2, 960)  # Exponential backoff with a max delay of 16 minutes (960 seconds)