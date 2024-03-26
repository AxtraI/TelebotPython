import telebot
import requests
from bs4 import BeautifulSoup
import psycopg2
from telebot import types

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
    keyboard.row('Получить мероприятия', 'Показать координаты на карте', 'FAQ', 'Пройти тест по профориентации')

    # Отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id, "Привет! Выберите действие:", reply_markup=keyboard)

# Обработчик кнопки FAQ
@bot.message_handler(func=lambda message: message.text == 'FAQ')
def faq(message):
    # Создаем клавиатуру для FAQ с кнопкой "Назад"
    faq_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    faq_keyboard.row('Перечень документов', 'Сроки подачи документов')
    faq_keyboard.row('Сроки приема оригинала документа об образовании', 'Приказы на зачисление')
    faq_keyboard.row('Вступительные испытания', 'Иногородним')
    faq_keyboard.row('Общежитие', 'Назад')

    # Отправляем сообщение с клавиатурой FAQ
    bot.send_message(message.chat.id, "Выберите интересующий вас раздел FAQ:", reply_markup=faq_keyboard)

# Обработчик кнопки "Назад" в разделе FAQ
@bot.message_handler(func=lambda message: message.text == 'Назад')
def back_to_start(message):
    start(message)
@bot.message_handler(func=lambda message: message.text == 'Перечень документов')
def document_list(message):
    documents = [
        "Удостоверение личности",
        "Документ об образовании",
        "Страховой номер индивидуального лицевого счета (СНИЛС)",
        "Согласие на зачисление",
        "Согласие законного представителя субъекта персональных данных на передачу персональных данных (субъекта) в электронном виде по открытым каналам сети Интернет",
        "Согласие поступающего на передачу персональных данных в электронном виде по открытым каналам сети Интерне"
    ]

    formatted_documents = "\n".join([f"{i + 1}. {doc}" for i, doc in enumerate(documents)])
    bot.send_message(message.chat.id, f"Перечень документов:\n{formatted_documents}")

@bot.message_handler(func=lambda message: message.text == 'Сроки подачи документов')
def document_deadlines(message):
    response = (
        "Прием документов с <b>20 июня 2024 года</b>:\n\n"
        "Бакалавриат (очная, очно-заочная и заочная форма обучения):\n"
        "- на бюджетные места по результатам ЕГЭ: – <b>по 25 июля</b>;\n"
        "- на бюджетные места по результатам внутренних испытаний – <b>по 10 июля</b>;\n"
        "- на платные места по результатам ЕГЭ – <b>по 19 августа</b>;\n"
        "- на платные места по результатам внутренних испытаний – <b>по 19 августа</b>;\n\n"
        "Магистратура:\n"
        "- на бюджетные места, очное, очно-заочное – <b>по 16 августа</b>;\n"
        "- на платные места, очное, очно-заочное – <b>по 28 августа</b>;\n"
        "- на бюджетные места, заочное – <b>по 23 августа</b>;\n"
        "- на платные места, заочное, - <b>не позднее, чем за 3 дня до начала учебного года</b> "
        "(Срок завершения приема документов устанавливается в соответствии с календарным учебным графиком)."
    )

    bot.send_message(message.chat.id, response, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == 'Сроки приема оригинала документа об образовании')
def original_document_deadlines(message):
    response = (
        "<b>Бакалавриат:</b>\n"
        "3 августа 2024 года до 17:00 по иркутскому времени завершается прием оригинала документа об образовании от лиц, включенных в списки поступающих, желающих быть зачисленными на основные бюджетные места;\n\n"
        "<b>Магистратура:</b>\n"
        "- 22 августа 2024 года до 17:00 по иркутскому времени - завершается прием оригиналов документов об образовании от поступающих на места в рамках контрольных цифр (бюджетные места) по очной, очно-заочной, набравшие наибольшее количество баллов."
    )

    bot.send_message(message.chat.id, response, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == 'Приказы на зачисление')
def admission_orders(message):
    response = (
        "<b>Приказы на зачисление:</b>\n\n"
        "<b>Бакалавриат:</b>\n"
        "- <b>30 июля</b> - на места в пределах особой, целевой и отдельной квот.\n"
        "- <b>06 августа</b> – на основные бюджетные места;\n"
        "- <b>31 августа</b> – на платные места;\n\n"
        "<b>Магистратура:</b>\n"
        "- <b>23 августа</b> – на бюджетные места, очное, очно-заочное;\n"
        "- <b>31 августа</b> – на платные места, очное, очно-заочное;\n"
        "- <b>29 августа</b> – на бюджетные места, заочное;\n"
        "- <b>31 августа</b> – на платные места, заочное."
    )

    bot.send_message(message.chat.id, response, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == 'Вступительные испытания')
def entrance_exams(message):
    response = (
        "<b>Вступительные испытания:</b>\n\n"
        "<b>Бакалавриат:</b>\n"
        "<b>Для поступающих на базе среднего общего образования:</b>\n"
        "Прием на все направления ведется по результатам Единого Государственного Экзамена (ЕГЭ):\n"
        "- Прикладная информатика: Русский язык, Математика, Информатика и ИКТ или Иностранный язык или Физика или Химия\n"
        "- Управление персоналом: Русский язык, Математика, Обществознание или Информатика и ИКТ или История или География\n"
        "- Сервис: Русский язык, Математика, Обществознание или Информатика и ИКТ или История или География\n"
        "- Реклама и связи с общественностью: Русский язык, Обществознание, История или Иностранный язык или Информатика и ИКТ\n"
        "- Туризм: Русский язык, История, Обществознание или Иностранный язык или География\n"
        "- Гостиничное дело: Русский язык, Обществознание, История или Иностранный язык\n\n"
        "<b>Для поступающих на базе среднего профессионального образования:</b>\n"
        "Прием на все направления ведется по результатам внутренних испытаний.\n\n"
        "<b>Магистратура:</b>\n"
        "Прием на все направления магистратуры ведется по результатам письменного междисциплинарного тестирования по соответствующему направлению."
    )

    bot.send_message(message.chat.id, response, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == 'Иногородним')
def out_of_town(message):
    response = (
        "<b>Иногородним:</b>\n\n"
        "На время поступления выделяется лишь незначительное количество мест в общежитии.\n"
        "Во время учебы общежитие предоставляется всем нуждающимся."
    )

    bot.send_message(message.chat.id, response, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == 'Общежитие')
def dormitory(message):
    response = (
        "<b>Общежитие:</b>\n\n"
        "<b>Шаг 1:</b> Оформите заявление на предоставление места в общежитии после предоставления оригиналов документов в приёмную комиссию. Образец заявления размещен на <a href='https://isu.ru/ru/about/facilities/hospices/index.html'>сайте университета</a>.\n\n"
        "При наличии категории, пользующейся льготами при распределении мест в общежитии, обязательно указывайте её и прикладывайте к заявлению подтверждающие документы. Перечень категорий, пользующихся льготами и необходимых документов размещен здесь.\n\n"
        "<b>Внимание!</b> Заявление на предоставления места в общежитии и документы, подтверждающие льготу, предоставляются на факультет/в институт до 19 августа.\n\n"
        "<b>Шаг 2:</b> Начиная с 24 августа, можете узнавать информацию о предоставлении места в общежитии в деканате, на сайте университета.\n\n"
        "<b>Шаг 3:</b> До оформления договора найма жилого помещения в студенческих общежитиях ознакомиться с Положением о студенческих общежитиях университета. Консультации Вы можете получить в управлении социальной и внеучебной работы (ул. Карла Маркса, 1, каб. 107, тел.: 521-509).\n\n"
        "<b>Шаг 4:</b> С 26 августа оформить в деканате факультета/института/отделения договор найма жилого помещения. Не забудьте взять паспорт!\n\n"
        "<b>Шаг 5:</b> После оформления договора найма жилого помещения нужно заселиться в общежитие и пройти медицинский осмотр. Адрес общежития уточните при оформлении договора в деканате факультета/института/отделения или на сайте университета.\n\n"
        "<b>Важно!</b> Для заселения в общежитие при себе необходимо иметь: паспорт, оригинал справки о флюорографии и 2 фотографии 3х4. Заселение в общежитие будет осуществляться с 26 августа по 15 сентября.\n\n"
        "Адрес общежития: г. Иркутск, ул. Улан-Баторская, 6а, общ. № 3"
    )

    bot.send_message(message.chat.id, response, parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == 'Показать координаты на карте')
def show_coordinates(message):
    destination = "52.250204,104.263723"  # Новые заданные координаты
    lon = destination.split(',')[1]
    lat = destination.split(',')[0]

    # Создаем ссылку на Яндекс.Карты с заданными координатами
    yandex_maps_link = f"https://yandex.ru/maps/?pt={lon},{lat}&z=14"

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
