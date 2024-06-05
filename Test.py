import telebot
import requests
from bs4 import BeautifulSoup
import sqlite3
import json
from telebot import types

TOKEN = '7096609931:AAGQeafGTfhz8H1266pH0sKP2P3YimTz_8k'
bot = telebot.TeleBot(TOKEN)
url = "http://sr.isu.ru/"

questions = [
    {"text": "Что вас больше всего привлекает в работе с людьми?",
     "image_url": "https://disk.yandex.ru/i/LRBjrcQFa07R6Q.jpg"},
    {"text": "Как вы относитесь к работе с большими объемами информации?",
     "image_url": "https://disk.yandex.ru/i/ph5lC_AglDfV4Q"},
    {"text": "Представьте, что вам нужно организовать мероприятие. Какой аспект вас больше всего волнует?",
     "image_url": "https://disk.yandex.ru/i/l9HI1_VUWFRHcg"},
    {"text": "Какие задачи вы предпочитаете: краткосрочные или долгосрочные проекты?",
     "image_url": "https://disk.yandex.ru/i/rGaiaPwqlITs8Q"},
    {"text": "Вас привлекает идея создания и ведения рекламных кампаний?",
     "image_url": "https://disk.yandex.ru/i/7YcGmmPHKU251A"}
]

answers = [
    ["Возможность помогать им в карьерном росте", "Использование коммуникаций для влияния на мнение",
     "Создание комфортной атмосферы", "Организация мероприятий", "Построение IT-решений для улучшения их работы"],
    ["Я предпочитаю анализировать информацию", "Использование информации для создания убедительных сообщений",
     "Организация данных для улучшения обслуживания клиентов", "Планирование маршрутов и логистики мероприятий",
     "Обработка и анализ данных для разработки программ"],
    ["Найм и обучение персонала для мероприятия", "Пиар и продвижение мероприятия",
     "Обеспечение высококачественного сервиса на мероприятии", "Создание увлекательной и насыщенной программы",
     "Техническая поддержка и цифровая инфраструктура мероприятия"],
    ["Долгосрочное планирование карьеры сотрудников", "Краткосрочные кампании и проекты",
     "Работа над текущими запросами клиентов", "Планирование сезонных туров",
     "Долгосрочная разработка и внедрение IT-проектов"],
    ["Нет, я предпочитаю заниматься развитием персонала", "Да, это моя страсть",
     "Мне интереснее работать напрямую с клиентами", "Мне больше нравится организация мероприятий",
     "Я предпочитаю работать над техническими аспектами"]
]


# Database initialization
def init_db():
    conn = sqlite3.connect('tests.db')
    cursor = conn.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS tests (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, questions TEXT)''')
    conn.commit()
    conn.close()


# Save a new test to the database
def save_test(name, questions):
    conn = sqlite3.connect('tests.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tests (name, questions) VALUES (?, ?)', (name, json.dumps(questions)))
    conn.commit()
    conn.close()


# Fetch all test names from the database
def get_all_tests():
    conn = sqlite3.connect('tests.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM tests')
    tests = cursor.fetchall()
    conn.close()
    return tests


# Fetch test questions by id
def get_test_questions(test_id):
    conn = sqlite3.connect('tests.db')
    cursor = conn.cursor()
    cursor.execute('SELECT questions FROM tests WHERE id = ?', (test_id,))
    questions = cursor.fetchone()
    conn.close()
    return json.loads(questions[0]) if questions else []


user_states = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    greeting = "Привет! Этот бот поможет тебе с профориентацией. Выбери действие ниже."
    bot.send_message(message.chat.id, greeting, reply_markup=main_keyboard())


@bot.message_handler(func=lambda message: message.text == 'Тестирование')
def handle_start_test(message):
    bot.send_message(message.chat.id, "Выберите тест для начала.", reply_markup=get_test_selection_keyboard())


def get_test_selection_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    tests = get_all_tests()
    for test_id, test_name in tests:
        keyboard.add(types.InlineKeyboardButton(text=test_name, callback_data=f'start_test:{test_id}'))
    keyboard.add(types.InlineKeyboardButton(text="Добавить новый тест", callback_data="add_new_test"))
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data.startswith("start_test:"))
def start_test(call):
    test_id = int(call.data.split(':')[1])
    chat_id = call.message.chat.id
    questions = get_test_questions(test_id)

    if questions:
        ensure_user_state(chat_id)
        user_states[chat_id]["question_index"] = 0
        user_states[chat_id]["results"] = {"Управление персоналом": 0, "Реклама и связи с общественностью": 0,
                                           "Сервис": 0, "Туризм": 0, "Прикладная информатика": 0}
        user_states[chat_id]["questions"] = questions
        ask_question(call.message)
    else:
        bot.send_message(chat_id, "Ошибка при загрузке теста. Попробуйте снова.")


@bot.callback_query_handler(func=lambda call: call.data == "add_new_test")
def add_new_test(call):
    bot.send_message(call.message.chat.id, "Отправьте JSON файл с тестом.")


@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.document.mime_type == 'application/json':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        try:
            test_data = json.loads(downloaded_file.decode('utf-8'))
            test_name = test_data.get("name", "Unnamed Test")
            questions = test_data.get("questions", [])

            if questions:
                save_test(test_name, questions)
                bot.send_message(message.chat.id, f"Тест '{test_name}' успешно добавлен.")
            else:
                bot.send_message(message.chat.id, "Неверный формат файла. Вопросы не найдены.")
        except json.JSONDecodeError:
            bot.send_message(message.chat.id, "Неверный формат файла. Загрузите правильный JSON файл.")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, загрузите файл в формате JSON.")


def ensure_user_state(chat_id):
    if chat_id not in user_states:
        user_states[chat_id] = {
            "question_index": 0,
            "results": {"Управление персоналом": 0, "Реклама и связи с общественностью": 0, "Сервис": 0, "Туризм": 0,
                        "Прикладная информатика": 0},
            "last_message_id": None,
            "last_photo_id": None,
            "questions": []
        }


def get_inline_keyboard(answers, question_index):
    keyboard = types.InlineKeyboardMarkup()
    for idx, answer in enumerate(answers):
        callback_data = f"answer:{question_index}:{idx}"
        keyboard.add(types.InlineKeyboardButton(text=answer, callback_data=callback_data))
    return keyboard


def ask_question(message):
    chat_id = message.chat.id
    question_index = user_states[chat_id]["question_index"]
    questions = user_states[chat_id]["questions"]

    if question_index < len(questions):
        question = questions[question_index]
        question_text = question['text']
        image_url = question.get('image_url', None)
        ans_options = answers[question_index]
        keyboard = get_inline_keyboard(ans_options, question_index)

        if image_url:
            if 'last_photo_id' in user_states[chat_id]:
                try:
                    bot.edit_message_media(media=types.InputMediaPhoto(image_url), chat_id=chat_id,
                                           message_id=user_states[chat_id]['last_photo_id'])
                except Exception as e:
                    if "message to edit not found" in str(e):
                        photo_message = bot.send_photo(chat_id, image_url)
                        user_states[chat_id]['last_photo_id'] = photo_message.message_id
                    else:
                        print(f"Failed to edit photo message: {e}")
            else:
                photo_message = bot.send_photo(chat_id, image_url)
                user_states[chat_id]['last_photo_id'] = photo_message.message_id

        if 'last_message_id' in user_states[chat_id]:
            try:
                bot.edit_message_text(text=question_text, chat_id=chat_id,
                                      message_id=user_states[chat_id]['last_message_id'], reply_markup=keyboard)
            except Exception as e:
                if "message to edit not found" in str(e):
                    msg = bot.send_message(chat_id, text=question_text, reply_markup=keyboard)
                    user_states[chat_id]['last_message_id'] = msg.message_id
                else:
                    print(f"Failed to edit question message: {e}")
        else:
            msg = bot.send_message(chat_id, text=question_text, reply_markup=keyboard)
            user_states[chat_id]['last_message_id'] = msg.message_id
    else:
        calculate_results(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("answer:"))
def process_answer(call):
    chat_id = call.message.chat.id
    data_parts = call.data.split(':')
    question_index = int(data_parts[1])
    answer_index = int(data_parts[2])
    direction_keys = ["Управление персоналом", "Реклама и связи с общественностью", "Сервис", "Туризм",
                      "Прикладная информатика"]
    direction = direction_keys[answer_index]

    ensure_user_state(chat_id)
    user_states[chat_id]["results"][direction] += 1
    user_states[chat_id]["question_index"] += 1

    ask_question(call.message)


def calculate_results(message):
    chat_id = message.chat.id
    if chat_id in user_states:
        results = user_states[chat_id]["results"]
        max_score = max(results.values())
        top_directions = [direction for direction, score in results.items() if score == max_score]

        if len(top_directions) > 1:
            response_text = "У вас одинаковое количество баллов в следующих направлениях: " + ", ".join(top_directions)
        else:
            response_text = f"Наиболее подходящее направление для вас: {top_directions[0]}"

        bot.send_message(chat_id, response_text)
        del user_states[chat_id]
    else:
        bot.send_message(chat_id, "Произошла ошибка. Пожалуйста, начните тест заново.")


# Function for parsing events from the URL
def parse_events_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        event_titles = soup.find_all('h4', class_='tribe-event-title')
        event_dates = soup.find_all('span', class_='tribe-event-date-start')

        if not event_titles and not event_dates:
            return "На данный момент не запланировано никаких мероприятий."

        events_data = []
        if len(event_titles) == len(event_dates):
            for title, date in zip(event_titles, event_dates):
                event_title = title.text.strip()
                event_date = date.text.strip()
                events_data.append({'title': event_title, 'date': event_date})
            return events_data if events_data else "На данный момент не запланировано никаких мероприятий."
        else:
            return "Количество заголовков и дат событий не совпадает."
    else:
        return f"Ошибка при получении страницы: {response.status_code}"


@bot.message_handler(func=lambda message: message.text == 'Мероприятия')
def get_events(message):
    events = parse_events_from_url(url)

    if isinstance(events, str):
        bot.send_message(message.chat.id, events)
    elif events:
        for event in events:
            response = f"Название мероприятия: {event['title']}\nДата мероприятия: {event['date']}"
            bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Произошла ошибка при загрузке мероприятий.")


# Main keyboard
def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Мероприятия', 'Корпус', 'Вопрос-Ответ', 'Тестирование', 'Веб-сайт', 'Контакты']
    keyboard.add(*buttons)
    return keyboard


@bot.message_handler(func=lambda message: message.text == 'Вопрос-Ответ')
def faq(message):
    faq_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    faq_keyboard.row('Перечень документов', 'Сроки подачи документов')
    faq_keyboard.row('Сроки приема оригиналов', 'Приказы на зачисление')
    faq_keyboard.row('Вступительные испытания', 'Иногородним')
    faq_keyboard.row('Общежитие', 'Назад')
    bot.send_message(message.chat.id, "Выберите интересующий вас раздел FAQ:", reply_markup=faq_keyboard)


@bot.message_handler(func=lambda message: message.text == 'Назад')
def back_to_start(message):
    bot.send_message(message.chat.id, "Возвращаемся в главное меню.", reply_markup=main_keyboard())


@bot.message_handler(func=lambda message: message.text == 'Перечень документов')
def document_list(message):
    documents = [
        "Удостоверение личности",
        "Документ об образовании",
        "Страховой номер индивидуального лицевого счета (СНИЛС)",
        "Согласие на зачисление",
        "Согласие законного представителя субъекта персональных данных на передачу персональных данных (субъекта) в электронном виде по открытым каналам сети Интернет",
        "Согласие поступающего на передачу персональных данных в электронном виде по открытым каналам сети Интернет"
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
        "- на платные места, заочное, - <b>не позднее, чем за 3 дня до начала учебного года</b> (Срок завершения приема документов устанавливается в соответствии с календарным учебным графиком)."
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


@bot.message_handler(func=lambda message: message.text == 'Корпус')
def show_coordinates(message):
    destination = "52.250204,104.263723"
    lon = destination.split(',')[1]
    lat = destination.split(',')[0]
    yandex_maps_link = f"https://yandex.ru/maps/?pt={lon},{lat}&z=14"

    bot.send_message(message.chat.id, f"Координаты {destination} на карте: {yandex_maps_link}")


@bot.message_handler(func=lambda message: message.text == 'Контакты')
def show_contacts(message):
    contact_info = (
        "г. Иркутск, ул. Лермонтова, 126\n"
        "(6 корпус ИГУ)\n\n"
        "Телефон для консультации:\n"
        "+7 (914) 927-91-29"
    )
    bot.send_message(message.chat.id, contact_info)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "Веб-сайт":
        bot.send_message(message.chat.id, "Посетите наш веб-сайт: [ИГУ](https://fbki-isu.ru/)", parse_mode="Markdown")


if __name__ == '__main__':
    init_db()
    bot.polling(non_stop=True)
