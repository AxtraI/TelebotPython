import telebot
import requests
from bs4 import BeautifulSoup
import psycopg2

TOKEN = '7096609931:AAGQeafGTfhz8H1266pH0sKP2P3YimTz_8k'
bot = telebot.TeleBot(TOKEN)
url = "http://sr.isu.ru/"
YANDEX_MAPS_API_KEY = 'cff25af7-4b9b-4d9f-b60a-ab0a3c110d9c'
ROUTE_URL = 'https://api.routing.yandex.net/v2/route'
YANDEX_MAPS_URL = 'https://yandex.ru/maps/?ll={lon},{lat}&z=14'

# Функция для парсинга мероприятий
def parse_events_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        event_titles = soup.find_all('h4', class_='tribe-event-title')
        event_dates = soup.find_all('span', class_='tribe-event-date-start')
        if len(event_titles) == len(event_dates):
            events_data = []
            for title, date in zip(event_titles, event_dates):
                event_title = title.text.strip()
                event_date = date.text.strip()
                events_data.append({'title': event_title, 'date': event_date})
            return events_data
        else:
            print("Количество заголовков и дат событий не совпадает")
    else:
        print("Ошибка при получении страницы:", response.status_code)

# Обработчик кнопки для получения мероприятий
@bot.message_handler(func=lambda message: message.text == 'Получить мероприятия')
def get_events(message):
    events = parse_events_from_url(url)

    if events:
        for event in events:
            response = f"Название мероприятия: {event['title']}\nДата мероприятия: {event['date']}"
            bot.send_message(message.chat.id, response)

# Остальной код бота остается без изменений
@bot.message_handler(commands=['start'])
def start(message):
    # Создаем клавиатуру
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    keyboard.row('Получить мероприятия', 'Показать координаты на карте')

    # Отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id, "Привет! Выберите действие:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == 'Показать координаты на карте')
def show_coordinates(message):
    destination = "52.249890,104.264603"  # Заданные координаты
    yandex_maps_link = YANDEX_MAPS_URL.format(lon=destination.split(',')[1], lat=destination.split(',')[0])

    bot.send_message(
        message.chat.id,
        f"Координаты {destination} на карте: {yandex_maps_link}"
    )

@bot.message_handler(content_types=['text'])
def findEmployee(message):
    if message.text == ">":
        pass
    else:
        con = psycopg2.connect(database='EmployeeDB', user='postgres', password='5055dom', host='localhost',
                               port='5432')
        cursor = con.cursor()

        message1 = message.text
        print(message1)
        likepattern = f"%{message1}%"

        cursor.execute("SELECT fio, job, email, phonenumber FROM employee WHERE job ILIKE %s", (likepattern,))

        container = cursor.fetchall()
        cursor.close()
        con.close()

        answer = ""
        for l in container:
            answer += f'ФИО: {l[0]} \n Должность: {l[1]} \n Телефон:{l[3]} \n Почта:{l[2]}'
            if len(answer) > 0:
                bot.send_message(message.chat.id, text=answer)
                answer = ""

if __name__ == '__main__':
    bot.polling(non_stop=True)
