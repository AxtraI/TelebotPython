import telebot

# Укажите токен вашего бота
TOKEN = '7096609931:AAGQeafGTfhz8H1266pH0sKP2P3YimTz_8k'

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# ID канала, из которого нужно получать сообщения
channel_username = '@fbki_isu'  # Замените на username вашего канала

# ID чата с пользователем, которому нужно отправлять сообщения
user_chat_id = '1556018153'  # Замените на ID чата с пользователем

# Обработчик команды /latestpost
@bot.message_handler(commands=['latestpost'])
def send_latest_post(message):
    try:
        # Получаем последнее обновление из канала
        updates = bot.get_updates()
        for update in updates:
            if update.channel_post and update.channel_post.chat.username == channel_username:
                latest_message = update.channel_post.text
                # Отправляем его пользователю
                bot.send_message(user_chat_id, latest_message)
                return
        # Если не найдено последнее сообщение, отправляем сообщение об ошибке
        bot.send_message(user_chat_id, "Последнее сообщение не найдено в канале.")
    except Exception as e:
        print("Error:", e)
        bot.send_message(user_chat_id, "Произошла ошибка при получении последнего сообщения из канала.")

# Запуск бота
bot.polling()
