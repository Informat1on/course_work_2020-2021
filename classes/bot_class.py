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
        # self.dispatcher.add_handler(callbackqueryhandler.CallbackQueryHandler(self.button))
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

        self.bot.send_message(text="Ищу книгу", chat_id=update.message.chat.id)
        self.bot.send_message(text="🔍", chat_id=update.message.chat.id)
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
        arr = [
            bookvoed, chitaina, combook, fitabooks, fkniga, labirint, mir_shkolnika, polka23
        ]

        cheap_book = {}
        cheap_book['price'] = 999999

        for i in arr:
            print(i)
            try:
                if (i['price'] is not None and i['price'] < cheap_book['price']):
                    cheap_book = i
                else:
                    continue
            except:
                pass

        print(cheap_book)
        # придумать обработку исключения, если где то нет данных, то вывести другой магазин
        # переработать условия и циклы для корректного вывода
        # где цена меньше там и выбираем
        # try:
        #     if labirint['price'] < chitai_gorod['price']:
        #         decision = labirint
        #         print(f"Цена на Лабиринт {labirint['price']} < цена на Читай Город {chitai_gorod['price']}")
        #
        #     else:
        #         decision = chitai_gorod
        #         print(f"Цена на Лабиринт {labirint['price']} > цена на Читай Город {chitai_gorod['price']}")
        # except:
        #     decision = self.findNone(chitai_gorod,labirint)[1]
        #     print(decision)
        #
        # # если нашло книгу
        # if decision is not None:
        #     # update.message.reply_text(labirint['name'])
        #     self.bot.send_photo(photo=decision['image'],
        #                         caption=f"{decision['name']}\n[Ссылка на книгу]({decision['link']})\nЦена книги: {decision['price']}₽",
        #                         chat_id=update.message.chat.id, parse_mode='Markdown')
        # # иначе
        # else:
        #     self.bot.send_message(text="По указанному названию книг не найдено 😥", chat_id=update.message.chat.id)
        #
        # # нужно вывести клавиатуру с надписью "найти снова"
        # # поработать с reply markup
        # self.bot.send_message(text="🔍 Для того, чтобы повторить поиск, введите название книги ниже: ",
        #                       chat_id=update.message.chat.id)

    def search(self, update, context):
        pass

    def findNone(self,arg1,arg2):
        # если в переменных есть значения
        if (bool(arg1) and bool(arg2) == True):
            return False
        # иначе есть какое то значение false
        else:
            # если первый аргумент пустой
            if bool(arg1) == False:
                return True, arg2
            #
            elif bool(arg2) == False:
                return True, arg1
            else:
                return True

    # функция отмены
    def cancel(self, update, context):
        user = update.message.from_user
        self.logger.info("User %s canceled the conversation.", user.first_name)
        update.message.reply_text('Bye! Hope to see you again next time.')

        return ConversationHandler.END
