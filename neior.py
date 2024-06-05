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

questions = [
    {"text":"Что вас больше всего привлекает в работе с людьми?","image_url": "https://disk.yandex.ru/i/LRBjrcQFa07R6Q.jpg"},
    {"text":"Как вы относитесь к работе с большими объемами информации?","image_url": "https://disk.yandex.ru/i/ph5lC_AglDfV4Q"},
    {"text":"Представьте, что вам нужно организовать мероприятие. Какой аспект вас больше всего волнует?","image_url": "https://disk.yandex.ru/i/l9HI1_VUWFRHcg"},
    {"text":"Какие задачи вы предпочитаете: краткосрочные или долгосрочные проекты?","image_url": "https://disk.yandex.ru/i/rGaiaPwqlITs8Q"},
    {"text":"Вас привлекает идея создания и ведения рекламных кампаний?","image_url": "https://disk.yandex.ru/i/7YcGmmPHKU251A"},
    {"text":"Насколько важна для вас возможность путешествовать в рамках работы?","image_url": "https://disk.yandex.ru/i/j37aWhlX2fr13w"},
    {"text":"Вас увлекает технология и постоянное обучение новым инструментам и программам?","image_url": "https://disk.yandex.ru/i/N_LGO8Dtg0v93A"},
    {"text":"Как вы относитесь к решению конфликтных ситуаций?","image_url": "https://disk.yandex.ru/i/7c2FBVOBp1jG5Q"},
    {"text":"Вам нравится анализировать данные и выявлять тренды?","image_url": "https://disk.yandex.ru/i/NT5VAbC6xXiPAg"},
    {"text":"Что для вас важнее в работе: креативность или систематичность?","image_url": "https://disk.yandex.ru/i/JWgCxBtiocg4cg"},
    {"text":"Вам интересно изучать различные культуры и языки?","image_url": "https://disk.yandex.ru/i/bNct99O1MZxAAg"},
    {"text":"Что вы предпочитаете: работать в команде или самостоятельно?","image_url": "https://disk.yandex.ru/i/IFpW0mfkuMfTTA"},
    {"text":"Представьте, что вы организуете социальную кампанию. Что для вас будет в приоритете?","image_url": "https://disk.yandex.ru/i/IS3db-08JrqZjw"},
    {"text":"Вас влечет идея создавать новые программы или приложения?","image_url": "https://disk.yandex.ru/i/95BGohu1gBNwuA"},
    {"text":"Чем бы вы предпочли заниматься: разработкой стратегий обучения или разработкой IT-систем?","image_url": "https://disk.yandex.ru/i/G1p9fmQrGyHM5A"},
    {"text":"Как вы оцениваете свою способность адаптироваться к изменениям?","image_url": "https://disk.yandex.ru/i/bfu78c8ojA1vxQ"},
    {"text":"Вам нравится ли работать с текстами и медийными материалами?","image_url": "https://disk.yandex.ru/i/saeYiIJQ89L7vg"},
    {"text":"Что для вас важнее в работе: прямое взаимодействие с людьми или анализ их данных?","image_url": "https://disk.yandex.ru/i/tRLEAN2SeaBFdQ"},
    {"text":"Какой тип задач вас больше привлекает: практические или теоретические?","image_url": "https://disk.yandex.ru/i/9Dv11C-CQtAw8w"},
    {"text":"Что вы предпочтете: планировать карьеру сотрудников или планировать технологические процессы?","image_url": "https://disk.yandex.ru/i/2iE75oWp7vyQtQ"},
    {"text":"Насколько важно для вас иметь гибкий график работы?","image_url": "https://disk.yandex.ru/i/sKvHB_t7E6lJUQ"},
    {"text":"Представьте, что вам нужно улучшить сервис компании. Какие первые шаги вы предпримете?","image_url": "https://disk.yandex.ru/i/uPteBtJGFX_fBA"},
    {"text":"Как вы относитесь к работе под давлением?","image_url": "https://disk.yandex.ru/i/HAsLo_GdfaBVZA"},
    {"text":"Вас интересует возможность работать в международной среде?","image_url": "https://disk.yandex.ru/i/3Vep1MvTU4rgMg"},
    {"text":"Что для вас важнее: стабильность или возможности для творчества?","image_url": "https://disk.yandex.ru/i/10DyrP7sPVn71Q"},
    {"text":"Вам нравится обучать и наставлять других?","image_url": "https://disk.yandex.ru/i/0sBAZhiqFLXp6A"},
    {"text":"Вы предпочитаете писать код или анализировать данные?","image_url": "https://disk.yandex.ru/i/IWcvVeltHJ3ywQ"},
    {"text":"Как вы относитесь к общению с прессой и участию в публичных мероприятиях?","image_url": "https://disk.yandex.ru/i/2bMYR-JlbmiFaw"},
    {"text":"Вам интересно работать над улучшением пользовательского опыта в приложениях и программах?","image_url": "https://disk.yandex.ru/i/OtzyJNkpdm-sJA"},
    {"text":"Что вам кажется более важным: развитие личных навыков или вклад в развитие компании?","image_url": "https://disk.yandex.ru/i/zIcer6aCmz6frQ"},

    # Добавьте все ваши вопросы здесь
]

# Варианты ответов
answers = [
    ["Возможность помогать им в карьерном росте", "Использование коммуникаций для влияния на мнение", "Создание комфортной атмосферы", "Организация мероприятий", "Создание IT-решений для улучшения работы"],
    ["Я предпочитаю анализировать информацию", "Использование информации для создания убедительных сообщений", "Организация данных для улучшения обслуживания клиентов", "Планирование маршрутов и логистики мероприятий", "Обработка и анализ данных для разработки программ"],
    ["Найм и обучение персонала для мероприятия", "Пиар и продвижение мероприятия", "Обеспечение высококачественного сервиса на мероприятии", "Создание увлекательной и насыщенной программы", "Техническая поддержка и цифровая инфраструктура мероприятия"],
    ["Долгосрочное планирование карьеры сотрудников", "Краткосрочные кампании и проекты", "Работа над текущими запросами клиентов", "Планирование сезонных туров", "Долгосрочная разработка и внедрение IT-проектов"],
    ["Нет, я предпочитаю заниматься развитием персонала", "Да, это моя страсть", "Мне интереснее работать напрямую с клиентами", "Мне больше нравится организация мероприятий", "Я предпочитаю работать над техническими аспектами"],
    ["Не очень важна, я предпочитаю стабильность", "Иногда это может быть интересно", "Редко бывает необходимо, но приятно", "Очень важна, я люблю новые места и культуры", "Не критично, больше важны технологии"],
    ["Мне интересно, но только в контексте управления", "Я предпочитаю фокусироваться на медиа и коммуникациях", "Важно, но не основное", "Технологии могут быть полезны в организации поездок", " Это моя страсть"],
    ["Это одна из моих ключевых задач", "Важно, чтобы улаживать вопросы с клиентами и партнерами", "Необходимо для обеспечения качественного сервиса", "Часть работы, особенно в сложных поездках", "Стараюсь избегать, предпочитаю работу с кодом"],
    ["Да, это помогает в стратегическом планировании персонала", "Это полезно для понимания эффективности кампаний", "Интересно, но не основная часть работы", "Полезно для планирования популярных направлений", "Это основа моей работы"],
    ["Систематичность в управлении персоналом", "Креативность в создании контента и кампаний", "Креативность в подходах к обслуживанию", "Креативность в создании туров", "Систематичность в разработке и тестировании"],
    ["Интересно, но не приоритетно", "Важно для понимания глобальных трендов", "Могу использовать это для улучшения сервиса", "Это моя страсть и основа профессии", "Интересно, если это связано с международными проектами"],
    ["В команде, ведь важно координировать действия персонала", "В команде, где каждый вносит свой вклад в общий проект", "В команде, чтобы предоставлять лучший сервис", "Самостоятельно, но с возможностью взаимодействия с другими", "Самостоятельно, большая часть работы требует концентрации"],
    ["Обеспечение справедливых условий труда", "Достигнуть максимального охвата и вовлеченности аудитории", "Предоставление высококлассного сервиса участникам", "Привлечение внимания к местным культурным особенностям", "Использование новейших технологий для распространения информации"],
    ["Нет, я предпочитаю работать с людьми напрямую", "Важно, если это помогает в коммуникациях", "Интересно, если это помогает улучшить сервис", "Использую программы, но не создаю", "Это основа моей работы"],
    ["Разработкой стратегий обучения", "Ни то, ни другое, мне интереснее коммуникации", "Разработкой систем улучшения сервиса", "Ни то, ни другое, я предпочитаю работу в туризме", "Разработкой IT-систем"],
    ["Хорошо адаптируюсь, чтобы помочь коллективу", "Легко адаптируюсь, особенно в изменяющихся трендах рынка", "Это важно для удовлетворения потребностей клиентов", "Адаптация к новым местам — часть работы", "Постоянно обучаюсь новым технологиям"],
    ["Предпочитаю работать с людьми напрямую", "Да, это основа моей работы", "Полезно для создания рекламы сервисов", "Использую для промоции туристических маршрутов", "Редко, больше фокус на технической документации"],
    ["Прямое взаимодействие, это суть моей работы", "Прямое взаимодействие для эффективных PR", "Взаимодействие с клиентами важно для качественного сервиса", "Прямое взаимодействие важно для организации путешествий", "Анализ данных, это ключ к эффективным решениям"],
    ["Практические, связанные с управлением персоналом", "Теоретические, связанные с изучением трендов", "Практические, направленные на улучшение обслуживания", "Практические, организация туров и мероприятий", "Теоретические, связанные с разработкой и аналитикой"],
    ["Карьеру сотрудников, это важно для их роста", "Ни то, ни другое, лучше создавать влиятельные кампании", "Технологические процессы в обслуживании", "Ни то, ни другое, лучше планировать путешествия", "Технологические процессы, это основа моей работы"],
    ["Важно, чтобы согласовывать с потребностями персонала", "Очень важно для встреч и мероприятий", "Полезно для работы с клиентами", "Необходимо для поездок и экскурсий", "Менее важно, больше ценю стабильный график"],
    ["Анализ потребностей и обратной связи сотрудников", "Исследование рынка и требований клиентов", "Переосмысление клиентского опыта и удовлетворенности", "Разработка новых туристических продуктов и услуг", "Внедрение новых технологий для автоматизации процессов"],
    ["Способен управлять стрессом в команде", "Это часть работы, особенно в срочных проектах", "Важно сохранять спокойствие и обеспечивать качество", "Умею адаптироваться и находить решения в дороге", "Предпочитаю систематизированный подход к решению проблем"],
    ["Да, это помогает понимать глобальные HR тренды", "Да, это расширяет возможности для кампаний", "Да, это улучшает понимание международных стандартов сервиса", "Обязательно, это суть работы в туризме", "Возможно, если это связано с международными IT проектами"],
    ["Стабильность в управлении персоналом", "Творчество в создании уникальных PR и рекламных проектов", "Творчество в предоставлении инновационного сервиса", "Творчество в разработке новых турпакетов", "Стабильность в разработке и поддержке систем"],
    ["Да, это основа работы с персоналом", "Интересно, если это связано с обучением коммуникациям", "Полезно для повышения уровня сервиса", "Важно для обучения гидов и сотрудников", "Люблю делиться знаниями по программированию"],
    ["Ни то, ни другое, мне важнее работа с людьми", "Ни то, ни другое, я склонен к творческим задачам", "Ни то, ни другое, мне ближе взаимодействие с клиентами", "Ни то, ни другое, я предпочитаю планировать и организовывать", "Предпочитаю писать код"],
    ["Не моя сфера, я фокусируюсь на внутреннем персонале", "Это часть моей работы, я это люблю", "Редко бывает необходимо, но я готов", "Иногда требуется для промоции туров", "Избегаю этого, предпочитаю работу за компьютером"],
    ["Нет, мне ближе работа с реальными людьми", "Нет, я фокусируюсь на визуальном и текстовом контенте", "Да, это важно для улучшения клиентского сервиса", "Интересно, если это помогает в туризме", "Да, это ключевая часть моей работы"],
    ["Развитие личных навыков, чтобы лучше управлять персоналом", "Вклад в развитие компании через эффективные PR стратегии", "Развитие личных навыков для предоставления лучшего сервиса", "Вклад в развитие компании через инновационные туры", "Равновесие между личным развитием и вкладом в технологии компании"],

    # Должно быть столько же списков, сколько вопросов
]

# Словарь для хранения результатов
user_states = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    greeting = "Привет! Этот бот поможет тебе с профориентацией. Выбери действие ниже."
    bot.send_message(message.chat.id, greeting, reply_markup=main_keyboard())


@bot.message_handler(func=lambda message: message.text == 'Тестирование')
def handle_start_test(message):
    bot.send_message(message.chat.id, "Нажмите кнопку ниже, чтобы начать тест. Если вы проходите тест с телефона, переверните телефон в горизонтальное положение для корректного отображения вопросов", reply_markup=get_start_keyboard())
def ensure_user_state(chat_id):
    if chat_id not in user_states:
        user_states[chat_id] = {
            "question_index": 0,
            "results": {
                "Управление персоналом": 0,
                "Реклама и связи с общественностью": 0,
                "Сервис": 0,
                "Туризм": 0,
                "Прикладная информатика": 0
            },
            "last_message_id": None,
            "last_photo_id": None
        }
@bot.callback_query_handler(func=lambda call: call.data == "start_test")
def start_test(call):
    chat_id = call.message.chat.id
    ensure_user_state(chat_id)
    user_states[chat_id]["question_index"] = 0  # сбросить индекс вопроса на начало
    user_states[chat_id]["results"] = {  # сбросить результаты
        "Управление персоналом": 0,
        "Реклама и связи с общественностью": 0,
        "Сервис": 0,
        "Туризм": 0,
        "Прикладная информатика": 0
    }
    ask_question(call.message)  # начать задавать вопросы



@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "start_test":
        start_test(call.message)
    elif call.data.startswith("answer:"):
        process_answer(call)

def get_inline_keyboard(answers, question_index):
    keyboard = types.InlineKeyboardMarkup()
    for idx, answer in enumerate(answers):
        callback_data = f"answer:{question_index}:{idx}"
        keyboard.add(types.InlineKeyboardButton(text=answer, callback_data=callback_data))
    return keyboard


def get_start_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Начать тест", callback_data="start_test"))
    return keyboard


def ask_question(message):
    chat_id = message.chat.id
    question_index = user_states[chat_id]["question_index"]
    if question_index < len(questions):
        question_text = questions[question_index]['text']
        image_url = questions[question_index]['image_url']
        ans_options = answers[question_index]
        keyboard = get_inline_keyboard(ans_options, question_index)

        # Пытаемся обновить существующее изображение, если оно уже было отправлено
        if 'last_photo_id' in user_states[chat_id]:
            try:
                bot.edit_message_media(media=types.InputMediaPhoto(image_url),
                                       chat_id=chat_id,
                                       message_id=user_states[chat_id]['last_photo_id'])
            except Exception as e:
                # Обрабатываем только ошибки, связанные с отсутствием сообщения
                if "message to edit not found" in str(e):
                    photo_message = bot.send_photo(chat_id, image_url)
                    user_states[chat_id]['last_photo_id'] = photo_message.message_id
                else:
                    print(f"Failed to edit photo message: {e}")
        else:
            # Отправляем новое изображение, если ранее не отправляли
            photo_message = bot.send_photo(chat_id, image_url)
            user_states[chat_id]['last_photo_id'] = photo_message.message_id

        # Пытаемся обновить текст вопроса
        if 'last_message_id' in user_states[chat_id]:
            try:
                bot.edit_message_text(text=question_text,
                                      chat_id=chat_id,
                                      message_id=user_states[chat_id]['last_message_id'],
                                      reply_markup=keyboard)
            except Exception as e:
                # Если обновление не удалось, проверяем причину и действуем соответственно
                if "message to edit not found" in str(e):
                    msg = bot.send_message(chat_id, text=question_text, reply_markup=keyboard)
                    user_states[chat_id]['last_message_id'] = msg.message_id
                else:
                    print(f"Failed to edit question message: {e}")
        else:
            # Отправляем сообщение, если ранее не отправляли
            msg = bot.send_message(chat_id, text=question_text, reply_markup=keyboard)
            user_states[chat_id]['last_message_id'] = msg.message_id



def process_answer(call):
    chat_id = call.message.chat.id
    data_parts = call.data.split(':')
    question_index = int(data_parts[1])
    answer_index = int(data_parts[2])
    direction_keys = ["Управление персоналом", "Реклама и связи с общественностью", "Сервис", "Туризм", "Прикладная информатика"]
    direction = direction_keys[answer_index]

    ensure_user_state(chat_id)
    user_states[chat_id]["results"][direction] += 1
    user_states[chat_id]["question_index"] += 1

    if user_states[chat_id]["question_index"] < len(questions):
        ask_question(call.message)
    else:
        calculate_results(call.message)
        user_states.pop(chat_id, None)  # Очищаем состояние после завершения теста


def calculate_results(message):
    chat_id = message.chat.id
    if chat_id in user_states:
        results = user_states[chat_id]["results"]
        max_score = max(results.values())  # Находим максимальное количество баллов
        top_directions = [direction for direction, score in results.items() if score == max_score]

        if len(top_directions) > 1:
            response_text = "У вас одинаковое количество баллов в следующих направлениях: " + ", ".join(top_directions)
        else:
            response_text = f"Наиболее подходящее направление для вас: {top_directions[0]}"

        bot.send_message(chat_id, response_text)
        del user_states[chat_id]  # Сброс состояния пользователя
    else:
        # Если состояние для данного chat_id не существует, отправляем уведомление
        bot.send_message(chat_id, "Произошла ошибка. Пожалуйста, начните тест заново.")



user_states = {}  # Инициализация состояния пользователей

# Функция для парсинга мероприятий
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
        # Если возвращается строка, отправляем её как сообщение
        bot.send_message(message.chat.id, events)
    elif events:
        # Если возвращается список событий, формируем ответ
        for event in events:
            response = f"Название мероприятия: {event['title']}\nДата мероприятия: {event['date']}"
            bot.send_message(message.chat.id, response)
    else:
        # Предусмотренный фоллбек на случай неожиданных результатов
        bot.send_message(message.chat.id, "Произошла ошибка при загрузке мероприятий.")



# Настройки для улучшенной клавиатуры
def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Мероприятия', 'Корпус', 'Вопрос-Ответ', 'Тестирование', 'Веб-сайт', 'Контакты']
    keyboard.add(*buttons)
    return keyboard

@bot.message_handler(
    func=lambda message: message.text.lower().startswith("find") or message.text.lower().startswith("найти"))
def find_employee(message):
    query = message.text.strip()
    print(f"Received message for search: '{query}'")

    if query and len(query.split()) > 1:  # Ensure there is something after 'find' or 'найти'
        search_term = query.split(' ', 1)[1]
        try:
            con = psycopg2.connect(database='EmployeeDB', user='postgres', password='5055dom', host='localhost',
                                   port='5432')
            cursor = con.cursor()

            likepattern = f"%{search_term}%"
            cursor.execute("SELECT fio, job, email, phonenumber FROM employee WHERE job ILIKE %s", (likepattern,))
            container = cursor.fetchall()

            cursor.close()
            con.close()

            if container:
                answer = "\n\n".join(
                    [f'ФИО: {l[0]}\nДолжность: {l[1]}\nТелефон: {l[3]}\nПочта: {l[2]}' for l in container])
                bot.send_message(message.chat.id, answer)
            else:
                bot.send_message(message.chat.id, "Сотрудников с данной должностью не найдено.")
        except Exception as e:
            bot.send_message(message.chat.id, f"Произошла ошибка при подключении к базе данных: {e}")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, укажите должность для поиска после 'find' или 'найти'.")



# Обработчик кнопки FAQ
@bot.message_handler(func=lambda message: message.text == 'Вопрос-Ответ')
def faq(message):
    # Создаем клавиатуру для FAQ с кнопкой "Назад"
    faq_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    faq_keyboard.row('Перечень документов', 'Сроки подачи документов')
    faq_keyboard.row('Сроки приема оригиналов', 'Приказы на зачисление')
    faq_keyboard.row('Вступительные испытания', 'Иногородним')
    faq_keyboard.row('Общежитие', 'Назад')

    # Отправляем сообщение с клавиатурой FAQ
    bot.send_message(message.chat.id, "Выберите интересующий вас раздел FAQ:", reply_markup=faq_keyboard)

# Обработчик кнопки "Назад" в разделе FAQ
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


@bot.message_handler(func=lambda message: message.text == 'Корпус')
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


@bot.message_handler(func=lambda message: message.text == 'Контакты')
def show_contacts(message):
    print("Контакты handler")
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
    bot.polling(non_stop=True)
