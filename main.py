import telebot
import pandas as pd
import io
from telebot.types import Message, CallbackQuery, InputFile
from typing import List
import os


class Answer:
    def __init__(self, username: str, first_answer: str, second_answer: str):
        self.username = username
        self.first_answer = first_answer
        self.second_answer = second_answer

    def to_dict(self):
        return {"username": self.username, "first_answer": self.first_answer, "second_answer": self.second_answer}


bot = telebot.TeleBot(bot_token)
privileged_users = ['BolyshayaMuxa']
all_answers: List[Answer] = []


@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text="Поехали", callback_data='start'))
    # if message.from_user.username in privileged_users:
    keyboard.add(telebot.types.InlineKeyboardButton(text="Скачать все ответы", callback_data='download'))
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}! Готов начать опрос?",
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    if call.data == 'start':
        if call.from_user.username in list(map(lambda answer: answer.username, all_answers)):
            bot.send_message(call.message.chat.id, f"Вы уже прошли опрос")
        else:
            first_question_handler(call)
    if call.data == 'download':
        download_answers(call)


def first_question_handler(call: CallbackQuery):
    sent_msg = bot.send_message(call.message.chat.id, f"Вопрос первый. Что думаешь насчет Лукойла?")
    bot.register_next_step_handler(sent_msg, second_question_handler)


def second_question_handler(message: Message):
    first_answer = message.text
    sent_msg = bot.send_message(message.chat.id, f"Вопрос второй. Ты честный человек?")
    bot.register_next_step_handler(sent_msg, end_question, first_answer)


def end_question(message: Message, first_answer):
    second_answer = message.text
    all_answers.append(Answer(message.from_user.username, first_answer, second_answer))
    bot.send_message(message.chat.id, f"Принято, спасибо за честность!")


def download_answers(call: CallbackQuery):
    df = pd.DataFrame(list(map(Answer.to_dict, all_answers)), columns=['username', 'first_answer', 'second_answer'])
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    buffer.seek(0)
    file = InputFile(buffer)
    file.file_name = "ответы.xlsx"
    bot.send_document(chat_id=call.message.chat.id, document=file, visible_file_name="Ответы.xlsx")


bot.polling(none_stop=True, interval=0)
