import psycopg2
import telebot
import requests
from bs4 import BeautifulSoup
from telebot import types

TOKEN="7096609931:AAGQeafGTfhz8H1266pH0sKP2P3YimTz_8k"
bot=telebot.TeleBot(TOKEN)
url = "http://sr.isu.ru/"

@bot.message_handler(commands=['start'])
def start(message):
    # Создаем клавиатуру
    bot.send_message(message.chat.id,"Привет, это бот ФБКИ ИГУ😉,пока что я умею немного,но я быстро учусь и скоро стану твоим незаменимым помошником!Пока что я могу только ответить на часто задаваемые вопросы, а так же ты можешь узнать у меня контактные данные специалистов нашего факультета, просто написав например:декан.")
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    keyboard.row('Получить мероприятия')

    # Отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id, "Так же ты можешь узнать ближайшие мероприятия", reply_markup=keyboard)

    # Переходим в состояние ожидания нажатия кнопки
    bot.register_next_step_handler(message, get_events)


@bot.message_handler(content_types=['text'])
def findEmployee(message):
    if (message.text==">"):
        pass
    else:
        con = psycopg2.connect(database='EmployeeDB', user='postgres', password='5055dom', host='localhost',
                               port='5432')
        cursor = con.cursor()

        message1 = message.text
        print(message1)
        likepattern = f"%{message1}%"

        # Use parameterized query to avoid SQL injection and string formatting issues
        cursor.execute("SELECT fio, job, email, phonenumber FROM employee WHERE job ILIKE %s", (likepattern,))

        container = cursor.fetchall()
        cursor.close()
        con.close()

        answer = ""
        for l in container:
            answer += f'ФИО: {l[0]} \n Должность: {l[1]} \n Телефон:{l[3]} \n Почта:{l[2]}'
            if len(answer) > 0:
                bot.send_message(message.chat.id, text=answer)
                answer=""


PARSE_STATE = 1


def get_events(message):
    if message.text == 'Получить мероприятия':
        url = 'http://sr.isu.ru/'
        events = parse_events_from_url(url)

        if events:
            for event in events:
                response = f"Название мероприятия: {event['title']}\nДата мероприятия: {event['date']}"
                bot.send_message(message.chat.id, response)

        # Удаляем клавиатуру
       # hide_keyboard = telebot.types.ReplyKeyboardRemove()
       # bot.send_message(message.chat.id,reply_markup=hide_keyboard)

        # Возвращаемся в состояние ожидания нажатия кнопки
        bot.register_next_step_handler(message, start)

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

# Запуск бота
if __name__ == '__main__':
    bot.polling()