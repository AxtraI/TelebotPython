import telebot
from telebot import types

# Токен вашего телеграм-бота
bot_token = '7096609931:AAGQeafGTfhz8H1266pH0sKP2P3YimTz_8k'

bot = telebot.TeleBot(bot_token)

# Словарь с вопросами и ответами
questions = {
    '1': {'text': 'Выберите картинку, которая больше всего вам нравится:',
          'options': ['https://cdn.media.marquiz.ru/v1/image/upload/upny8aaawrdlhqbw1nix.png?format=webp&func=auto&fit=cover&width=420&height=420&dpr=1', 'https://cdn.media.marquiz.ru/v1/image/upload/oi7x7ktudtpkyykhjvfi.png?format=webp&func=auto&fit=cover&width=420&height=420&dpr=1']},
    '2': {'text': 'Какое изображение вызывает у вас наибольший интерес?',
          'options': ['https://cdn.media.marquiz.ru/v1/image/upload/vjny3hbzdflcxkekvix0.png?format=webp&func=auto&fit=cover&width=420&height=420&dpr=1', 'https://cdn.media.marquiz.ru/v1/image/upload/joikabxin8wcytjk9wxp.png?format=webp&func=auto&fit=cover&width=420&height=420&dpr=1']},
    # Добавьте дополнительные вопросы и изображения по мере необходимости
}

# Словарь с ответами пользователей
user_answers = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    send_question(message.chat.id, '1')

# Обработчик inline-кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    user_answers[user_id] = call.data
    next_question_number = str(int(call.data) + 1)
    if next_question_number in questions:
        send_question(user_id, next_question_number)
    else:
        bot.send_message(user_id, "Спасибо за прохождение теста!")

# Функция для отправки вопроса
def send_question(chat_id, question_number):
    question_data = questions[question_number]
    for option in question_data['options']:
        bot.send_photo(chat_id, option)
    markup = types.InlineKeyboardMarkup(row_width=2)
    for i, option in enumerate(question_data['options']):
        button = types.InlineKeyboardButton(str(i + 1), callback_data=question_number)
        markup.add(button)
    bot.send_message(chat_id, question_data['text'], reply_markup=markup)

# Запуск бота
bot.polling()