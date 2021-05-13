# импортирую библиотеку запросов
import requests
# импортирую библиотеку для работы с парсингом страницы
from bs4 import BeautifulSoup
# импортирую библиотеку для работы с браузер модом
from selenium import webdriver
# импортирую библиотеку для работы с api Telegram
import telegram
# импортирую библиотеку для логов
import logging
# импортирую объекты для работы с клавиатурой
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, callbackqueryhandler)
import time
from modules import bookvoed as bk, chitaina as cht, combook as cmbk, fitabooks as fitb, fkniga as fkng, labirint as lbrn, polka23 as pl23, mir_shkolnika as mrshk


class FindBookBot:
    # конструктор класса
    def __init__(self, bot_token):
        self.bot = telegram.Bot(token=bot_token)  # создаю бота
        self.updater = Updater(token=bot_token)  # добавляем апдейтер
        self.dispatcher = self.updater.dispatcher  # добавляем диспатчер
        self.message_id = '' #id удаляемого сообщения
        self.arr = [] #массив эл-ов
        # обьяляю состояния
        self.BUTTON_BEGIN, self.BOOK_NAME, self.SEARCH, self.END = range(4)

        # Включить ведение журнала
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    # функция старта бота
    def start(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        print(self.bot.get_me())  # проверка бота на валидность

        # обработчик состояний
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.begin)],

            states={
                self.BUTTON_BEGIN: [CommandHandler('start', self.begin), MessageHandler(Filters.text, self.button)],
                self.BOOK_NAME: [CommandHandler('start', self.begin), MessageHandler(Filters.text, self.book_name)],
                self.SEARCH: [CommandHandler('start', self.begin), MessageHandler(Filters.text, self.search)]
            },

            fallbacks=[CommandHandler('cancel', self.cancel)]
        )

        self.dispatcher.add_handler(conv_handler)
        # лог всех ошибок
        self.dispatcher.add_error_handler(self.error)
        # query handler
        self.dispatcher.add_handler(callbackqueryhandler.CallbackQueryHandler(self.callback_butt))
        self.updater.start_polling()

    # функция приветствия
    def begin(self, update, context):
        reply_keyboard = [['Найти книгу 🔍']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text("Привет, меня зовут BestBookFinder! Для того, чтобы найти книгу,"
                                  " нажми кнопку снизу: ", reply_markup=markup)

        return self.BUTTON_BEGIN

    # функция обработки ошибок
    def error(self, update, context):
        self.logger.warning('Update "%s" caused error "%s"', update, context.error)

    # функция обработки кнопки
    def button(self, update, context):
        # отправляю запрос о вводе названия и убираю клавиатуру
        self.bot.send_message(text="Введите название книги: ", chat_id=update.message.chat.id,
                              reply_markup=ReplyKeyboardRemove())
        # перехожу на другое состояние
        return self.BOOK_NAME

    # функция обработки имени автора
    def book_name(self, update, context):

        book_name = update.message.text
        print(f'Начало поиска книг по названию {book_name}')

        self.bot.send_message(text="Ищу книгу 🔍", chat_id=update.message.chat.id)
        # self.bot.send_message(text="🔍", chat_id=update.message.chat.id)

        # кидаю в переменную лабиринт словарь с единственным элементом - смая дешевая книга и ее метаданные
        # присваиваю переменным словари, в которых находятся самые дешевае книги и их параметры

        bookvoed = bk.main(book_name)
        chitaina = cht.main(book_name)
        combook = cmbk.main(book_name)
        fitabooks = fitb.main(book_name)
        fkniga = fkng.main(book_name)
        labirint = lbrn.main(book_name)
        mir_shkolnika = mrshk.main(book_name)
        polka23 = pl23.main(book_name)
        self.arr = [
            bookvoed, chitaina, combook, fitabooks, fkniga, labirint, mir_shkolnika, polka23
        ]

        cheap_book = {}
        cheap_book['price'] = 999999

        for i in self.arr:
            # print(i)
            try:
                if (i['price'] is not None and i['price'] < cheap_book['price']):
                    cheap_book = i
                else:
                    continue
            except:
                pass

        # если нашло хоть 1 книгу
        if (cheap_book['price'] < 999999):
            print(cheap_book)
            wrong_button = InlineKeyboardButton(text='Не та книга ? :c',callback_data='wrong')
            # self.bot.send_photo(photo=cheap_book['image'],chat_id=update.message.chat.id)
            self.bot.send_message(
                # photo=cheap_book['image'],
                text=f"{cheap_book['name']}\n[Ссылка на книгу]({cheap_book['link']})\nЦена книги: {cheap_book['price']}₽",
                chat_id=update.message.chat.id, parse_mode='Markdown',reply_markup=InlineKeyboardMarkup([[wrong_button]]))
        # если не нашло ни одной
        else:
            self.bot.send_message(text=f"По указанному названию '{book_name}' книг не найдено 😥", chat_id=update.message.chat.id)


        # # нужно вывести клавиатуру с надписью "найти снова"
        # # поработать с reply markup
        self.bot.send_message(text="🔍 Для того, чтобы повторить поиск, введите название книги ниже: ",
                              chat_id=update.message.chat.id)

    def search(self, update, context):
        pass

    def callback_butt(self,update,context):
        query = update.callback_query

        # если нашло неправильную книгу
        if (query.data == 'wrong'):
            reply_markup = []
            for i in range(len(self.arr)):
                if (self.arr[i].keys()):
                    # print(i)
                    # print(i['name'])
                    try:
                        reply_markup.append(
                            [InlineKeyboardButton(text=f"{self.arr[i]['name']} - {self.arr[i]['price']}₽", callback_data=str(i))])
                    except:
                        pass

            query.edit_message_text(text="Выберите книгу",reply_markup=InlineKeyboardMarkup(reply_markup))


        try:
            if (int(query.data) >= 0 and int(query.data) <= len(self.arr)):
                # отправить заново карточку с книгой
                wrong_button = InlineKeyboardButton(text='Не та книга ? :c', callback_data='wrong')
                query.edit_message_text(
                    # photo=cheap_book['image'],
                    text=f"{self.arr[int(query.data)]['name']}\n[Ссылка на книгу]({self.arr[int(query.data)]['link']})\nЦена книги: {self.arr[int(query.data)]['price']}₽",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([[wrong_button]]))

        except:
            pass
        else:
            pass

    # функция отмены
    def cancel(self, update, context):
        user = update.message.from_user
        self.logger.info("User %s canceled the conversation.", user.first_name)
        update.message.reply_text('Bye! Hope to see you again next time.')

        return ConversationHandler.END
