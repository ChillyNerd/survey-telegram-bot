import telebot
import pandas as pd
import io
import logging
from threading import Lock
from telebot.types import Message, CallbackQuery, InputFile
from src.answer import Answer
from typing import List


class Bot:
    def __init__(self, token: str, questions: List[str], privileged_users: List[str] = None):
        self.__bot = telebot.TeleBot(token)
        self.questions: List[str] = questions
        self.privileged_users: List[str] = privileged_users
        self.__all_answers: List[Answer] = []
        self.__log = logging.getLogger("SurveyBot")
        self.__lock = Lock()
        self.__init_callbacks()

    def __init_callbacks(self):
        @self.__bot.message_handler(commands=['start'])
        def send_welcome(message: Message):
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton(text="Поехали", callback_data='start'))
            if self.privileged_users is None or message.from_user.username in self.privileged_users:
                keyboard.add(telebot.types.InlineKeyboardButton(text="Скачать все ответы", callback_data='download'))
            self.__bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}! Готов начать опрос?",
                                    reply_markup=keyboard)

        questions_length = len(self.questions)
        if questions_length == 0:
            return

        def question_handler_template(current_question: str, next_step, first_question=False):
            if first_question:
                def question_handler(call: CallbackQuery):
                    sent_msg = self.__bot.send_message(call.message.chat.id, current_question)
                    self.__bot.register_next_step_handler(sent_msg, next_step)
            else:
                def question_handler(message: Message, *args):
                    answer = message.text
                    sent_msg = self.__bot.send_message(message.chat.id, current_question)
                    self.__bot.register_next_step_handler(sent_msg, next_step, *[*args, answer])
            return question_handler

        def end_question_handler(message: Message, *args):
            with self.__lock:
                self.__all_answers.append(Answer(message.from_user.username, *[*args, message.text]))
                self.__log.info(f"Saved {message.from_user.username} answer")
            self.__bot.send_message(message.chat.id, f"Принято, спасибо за честность!")

        for index, question in enumerate(self.questions[::-1]):
            if index == 0:
                next_question = end_question_handler
            else:
                next_question = self.__getattribute__(f'question_{questions_length - index + 1}')
            self.__setattr__(
                f'question_{questions_length - index}',
                question_handler_template(question, next_question, index == questions_length - 1)
            )

        @self.__bot.callback_query_handler(func=lambda call: True)
        def callback_query(call: CallbackQuery):
            if call.data == 'start':
                if call.from_user.username in list(map(lambda answer: answer.username, self.__all_answers)):
                    self.__bot.send_message(call.message.chat.id, f"Вы уже прошли опрос")
                else:
                    self.__getattribute__("question_1")(call)
            if call.data == 'download':
                download_answers(call)

        def download_answers(call: CallbackQuery):
            df = pd.DataFrame(list(map(Answer.to_dict, self.__all_answers)))
            df.columns = ['user', *self.questions]
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Sheet1', index=False)
            buffer.seek(0)
            file = InputFile(buffer)
            self.__bot.send_document(chat_id=call.message.chat.id, document=file, visible_file_name="Ответы.xlsx")

    def start(self):
        self.__bot.polling(none_stop=True, interval=0)
