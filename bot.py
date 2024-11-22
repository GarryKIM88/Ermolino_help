import uuid
import struct
import telebot
import random
from telebot import types
# Пересылка сообщений
admin = 5750767901 #Мой РАБОЧИЙ ID
my = 5272284427 #Мой ID
stas = 723472573#Стаса ID

# Загружаем список дежурных
f = open('.venv/Ermolino_help/data/text/officer.txt', 'r', encoding='UTF-8')
officer = f.read().split('\n')
f.close()

# Загружаем список информации
f = open('.venv/Ermolino_help/data/text/manual.txt', 'r', encoding='UTF-8')
manual  = f.read().split('\n')
f.close()

# Создаем бота
bot = telebot.TeleBot('7716310474:AAGbeWwLZh84lPeXo7M9J-UJD0_Z_LwpeWo')

# Получить ID чата при отправке сообщения /id
@bot.message_handler(commands=["id"]) 
def chat_id(message):
    my_chat_id = int(message.chat.id)
    bot.send_message(message.chat.id, my_chat_id)

# Команда start
@bot.message_handler(commands=["start"])
def start(message):
# Добавляем кнопки
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Не работает', 'Полезное')
    user_markup.row('Кто дежурный?')
    bot.send_message(message.from_user.id, 'Нажми: \nКто дежурный и узнаете кто дежурит на этой неделе\nПолезное и узнаете что то новое ', reply_markup=user_markup)

# Ответ на 
@bot.message_handler(func=lambda message: message.text=='Не работает')
def buton(message):
# Добавляем кнопки
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Дисплей покупателя', 'Сканер ШК')
    user_markup.row('Меню')
    bot.send_message(message.from_user.id, 'Выберите что у вас не работает', reply_markup=user_markup)
# Возврат 
@bot.message_handler(func=lambda message: message.text=='Меню')
def menu(message):
    start(message)

# Ответ на Кто дежурный
@bot.message_handler(func=lambda message: message.text=='Кто дежурный?')
def dej(message):
    answer = officer
    bot.send_message(message.chat.id, answer)
# Ответ на Полезное
@bot.message_handler(func=lambda message: message.text=='Полезное')
def inf(message):
    answer = manual
    bot.send_message(message.chat.id, answer)

# Пересылка текста 
@bot.message_handler(content_types=["text"])
def handle_text(message):
    msg = "Пользователь {} {} ID {} @{} написал \"{}\".".format(message.from_user.first_name, message.from_user.last_name, message.from_user.id, message.from_user.username,  message.text) # Подпись
    bot.send_message(admin, msg) 
   
# Обработка фотографии  
def process(filename):
    pass
@bot.message_handler(content_types=['photo'])
def photo(message):
    # скачивание файла
    file_id = message.photo[-1].file_id
    path = bot.get_file(file_id)
    downloaded_file = bot.download_file(path.file_path)
    # узнаем расширение и случайное придумываем имя
    extn = '.' + str(path.file_path).split('.')[-1]
    name = '.venv/Ermolino_help/data/images/' + str(uuid.uuid4()) + extn
    # создаем файл и записываем туда данные
    with open(name, 'wb') as new_file:
        new_file.write(downloaded_file)
    # обрабатываем картинку фильтром
    process(name)
    # открываем файл и отправляем его пользователю
    with open(name, 'rb') as new_file:
        msg = "Пользователь {} {} ID {} @{} прислал фото..".format(message.from_user.first_name, message.from_user.last_name, message.from_user.id, message.from_user.username,  message.text) # Подпись
        bot.send_message(admin, msg) 
        bot.send_photo(admin, new_file.read()) 

# Обрабатка стикера
stickers = []
@bot.message_handler(content_types=['sticker'])
def echo(message):
    sticker = message.sticker.file_id
    stickers.append(sticker)
    msg = "Пользователь {} {} ID {} @{} прислал стикер..".format(message.from_user.first_name, message.from_user.last_name, message.from_user.id, message.from_user.username,  message.text) # Подпись
    bot.send_message(admin, msg) 
    bot.send_sticker(admin,random.choice(stickers))


# обработка аудио
def download_audio(message):
    voice_id = message.voice.file_id
    file_description = bot.get_file(voice_id)
    downloaded_file = bot.download_file(file_description.file_path)

    filename = '.venv/Ermolino_help/data/audio/' + str(uuid.uuid4()) + '.oga'

    with open(filename, 'wb') as file:
        file.write(downloaded_file)

    return filename

def convert_audio(path):
    import subprocess
    src_filename = path
    dest_filename = path + '.wav'

    subprocess.run(['ffmpeg', '-i', src_filename, dest_filename])
    return dest_filename

def speed_up(path):
    import wave

    audio = wave.open(path)
    data = audio.readframes(audio.getnframes())
    values = struct.unpack(f'<{ len(data) // 2 }h', data)
    values2 = []
    for i in range(0, len(values), 2):
        values2.append(values[i])

    data = struct.pack(f'<{ len(values2) }h', *values2)

    audio2 = wave.open(path + '.2.wav', 'wb')
    audio2.setnchannels(audio.getnchannels())
    audio2.setframerate(audio.getframerate())
    audio2.setsampwidth(audio.getsampwidth())
    audio2.writeframes(data)

    return path + '.2.wav'

@bot.message_handler(content_types=['voice'])
def voice(message):
    path = download_audio(message)
    path = convert_audio(path)
    path = speed_up(path)

    
    bot.send_audio(message.chat.id, open(path, 'rb').read())
    print(path)

# Запускаем бота
bot.polling(none_stop=True, interval=0)
