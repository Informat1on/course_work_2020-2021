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
import modules.labirint as Labirint


class FindBookBot:
    # конструктор класса
    def __init__(self, bot_token):
        self.bot = telegram.Bot(token=bot_token)  # создаю бота
        self.updater = Updater(token=bot_token)  # добавляем апдейтер
        self.dispatcher = self.updater.dispatcher  # добавляем диспатчер
        # обьяляю состояния
        self.BUTTON_BEGIN, self.AUTHOR, self.SEARCH, self.END = range(4)

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
                self.AUTHOR: [CommandHandler('start', self.begin), MessageHandler(Filters.text, self.author)],
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
        return self.AUTHOR

    # функция обработки имени автора
    def author(self, update, context):
        book_name = update.message.text
        print(f'Начало поиска книг по названию {book_name}')

        self.bot.send_message(text="Ищу книгу", chat_id=update.message.chat.id)
        self.bot.send_message(text="🔍", chat_id=update.message.chat.id)
        # кидаю в переменную лабиринт словарь с единственным элементом - смая дешевая книга и ее метаданные
        # присваиваю переменным словари, в которых находятся самые дешевае книги и их параметры
        labirint = Labirint.main('some name')
        chitai_gorod = self.chitai_gorod(book_name)

        print(bool(chitai_gorod))
        print(bool(labirint))

        # придумать обработку исключения, если где то нет данных, то вывести другой магазин
        # переработать условия и циклы для корректного вывода
        # где цена меньше там и выбираем
        try:
            if labirint['price'] < chitai_gorod['price']:
                decision = labirint
                print(f"Цена на Лабиринт {labirint['price']} < цена на Читай Город {chitai_gorod['price']}")

            else:
                decision = chitai_gorod
                print(f"Цена на Лабиринт {labirint['price']} > цена на Читай Город {chitai_gorod['price']}")
        except:
            decision = self.findNone(chitai_gorod,labirint)[1]
            print(decision)

        # если нашло книгу
        if decision is not None:
            # update.message.reply_text(labirint['name'])
            self.bot.send_photo(photo=decision['image'],
                                caption=f"{decision['name']}\n[Ссылка на книгу]({decision['link']})\nЦена книги: {decision['price']}₽",
                                chat_id=update.message.chat.id, parse_mode='Markdown')
        # иначе
        else:
            self.bot.send_message(text="По указанному названию книг не найдено 😥", chat_id=update.message.chat.id)

        # нужно вывести клавиатуру с надписью "найти снова"
        # поработать с reply markup
        self.bot.send_message(text="🔍 Для того, чтобы повторить поиск, введите название книги ниже: ",
                              chat_id=update.message.chat.id)

    def chitai_gorod(self, book_name):
        try:
            # book_name = 'муму'
            book_name = book_name.replace(' ', '%20')
            # source = requests.get(f'https://www.chitai-gorod.ru/search/result/?q={book_name}',headers=self.headers,proxies=self.proxies)
            browser = webdriver.Chrome()
            browser.get(f'https://www.chitai-gorod.ru/search/result/?q={book_name}')
            source = browser.page_source
            # нужно предварительно написать pip install bs4 и lxml
            soup = BeautifulSoup(source, 'lxml')

            # так как страниц несколько, то нужно пробежаться по всем им
            # количество страниц
            pages = soup.find_all('a', attrs={'class': 'pagination-item js__pagination_item'})
            pages = len(pages)


            soup = soup.find_all('div', attrs={'class': 'product-card js_product js__product_card'})
            print('Ищу книги')
            # print(soup)

            # автор и название книги - 1 выведенная книга в поиске, тк поиск на 100% точный
            book = soup[0].find('div', attrs={'class': 'product-card__title js-analytic-product-title'}).text
            author = soup[0].find('div', attrs={'class': 'product-card__author'}).text

            # минимальная цена книги
            min_price = 9999999
            # словарь для хранения данных о самой дешевой книге
            cheap_book = {}
            for index in range(0, pages):
                browser.get(f'https://www.chitai-gorod.ru/search/result/?q={book_name}&page={index+1}')
                source = browser.page_source
                time.sleep(0.5)
                soup = BeautifulSoup(source, 'lxml')
                soup = soup.find_all('div', attrs={'class': 'product-card js_product js__product_card'})

                for i in range(len(soup)):
                    print(f'page is {index} and item is {i}')
                    try:
                        curr_book = soup[i].find('div',
                                                 attrs={'class': 'product-card__title js-analytic-product-title'}).text
                        # ошибка возникает на авторе
                        curr_author = soup[i].find('div', attrs={'class': 'product-card__author'}).text
                    except:
                        continue

                    # если это нужный автор и книга
                    if author in curr_author:
                        if book in curr_book:
                            # если есть возможность купить
                            try:
                                if ('Купить' in soup[i].find('span', attrs={'class': 'js__card_button_text'}).text) or (
                                        'купить' in soup[i].find('span', attrs={'class': 'js__card_button_text'}).text):

                                    # достаю цену
                                    try:
                                        price = int(soup[i].find('span', attrs={'class': 'price'}).text.split(' ')[0])
                                    except:

                                        continue
                                    # если цена меньше минимальной, то теперь минимальная цена - цена этого товара
                                    if price < min_price:
                                        min_price = price
                                    else:
                                        continue
                                    cheap_book['name'] = f'{author} - {book}'
                                    cheap_book[
                                        'link'] = f"https://www.chitai-gorod.ru{soup[i].find('a', attrs={'class': 'product-card__link js-watch-productlink'})['href']}"
                                    cheap_book['price'] = price
                                    cheap_book['image'] = f"{soup[i].find('img')['data-src']}"
                            except:
                                pass

                                print(f"{author} - {book} # price is {min_price} #link is {cheap_book['link']} # image is {cheap_book['image']}")
            browser.close()
            return cheap_book
        except:
            return None

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
