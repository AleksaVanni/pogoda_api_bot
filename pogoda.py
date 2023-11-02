import telebot
import requests
import json
from telebot import types
from decouple import config
import logging


# TOKEN = config('TOKEN')
bot = telebot.TeleBot(TOKEN)
# API = config('API')


# Настройка логирования
logging.basicConfig(filename="bot.log", level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Добро пожаловать! Напишите название города, чтобы узнать погоду.')


# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def get_weather(message):
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')

    if res.status_code == 200:
        data = json.loads(res.text)
        try:
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            send_weather_info(message.chat.id, city, temp, description)
        except KeyError as e:
            logging.error(f"Ошибка при обработке ответа от API: {e}")
            bot.reply_to(message, "Произошла ошибка при обработке ответа от API.")
    else:
        logging.error(f"Ошибка при запросе к API: {res.status_code}")
        bot.reply_to(message, "Город не найден. Пожалуйста, уточните название города.")


# Отправка информации о погоде и изображения
def send_weather_info(chat_id, city, temp, description):
    bot.send_message(chat_id, f'Сейчас в городе {city.title()}: {temp} градусов, {description}.')

    if description == 'clear sky':
        image = 'image/sunny.png'
    elif description == 'broken clouds':
        image = 'image/sun.png'
    elif description == 'overcast clouds':
        image = 'image/overcast_clouds.png'
    elif description == 'mist':
        image = 'image/tuman.png'
    elif description == 'light rain' or description == 'moderate rain' or description == 'light intensity shower rain':
        image = 'image/rain.png'
    elif description == 'wind':
        image = 'image/wind.png'
    else:
        print("в доработке")
        image = 'image/cat.png'

    try:
        with open(image, 'rb') as file:
            bot.send_photo(chat_id, file)
    except FileNotFoundError as e:
        logging.error(f"Изображение не найдено: {e}")
        bot.send_message(chat_id, "Изображение не найдено.")


# Обработчик неизвестных команд и текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    bot.reply_to(message, "Извините, я не понимаю ваш запрос. Пожалуйста, воспользуйтесь командой /start для начала.")


# Обработчик команды /help
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Для получения информации о погоде, введите название города. Например, "Москва".')


# if __name__ == "__main__":
bot.polling(none_stop=True)
