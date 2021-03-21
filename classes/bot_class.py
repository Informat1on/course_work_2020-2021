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


class FindBookBot:
    # конструктор класса
    def __init__(self, bot_token):
        self.bot = telegram.Bot(token=bot_token)  # создаю бота
        self.updater = Updater(token=bot_token)  # добавляем апдейтер
        self.dispatcher = self.updater.dispatcher  # добавляем диспатчер
        # заголовки для парсинга
        self.headers = {
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}

        # обьяляю состояния
        self.BUTTON_BEGIN, self.AUTHOR, self.SEARCH, self.END = range(4)

        # Включить ведение журнала
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.proxies = {
            'http': 'http://MYMpC4:2Hvu2A@194.67.214.169:9780',
            'https': 'http://MYMpC4:2Hvu2A@194.67.214.169:9780',
        }

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
        labirint = self.labirint(book_name)
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



    # РАБОЧАЯ ФУНКЦИЯ ЛАБИРИНТ
    def labirint(self, book_name):
        # book_name = 'мастер и маргарита'
        book_name_edited = book_name.replace(' ', '%20')
        source = requests.get(f'https://www.labirint.ru/search/{book_name_edited}/'
                              f'?stype=0&available=1&preorder=1&paperbooks=1', headers=self.headers).text
        soup = BeautifulSoup(source, 'lxml')

        # пытаюсь найти ошибку в поиске
        try:
            h1 = soup.find('div', attrs={'class': 'search-error'}).find('h1').text
            return None

        # если ошибок нет
        except:
            soup = soup.find_all('div', attrs={'class': 'card-column'})

            # выбираем самую первую книгу, тк это 100% совпадение
            # и берем с этой книги название + автора отдельно, чтобы отсеять всякие рецензии и прочее ненужное
            origin_book = soup[0].find('a', attrs={'class': 'cover'})['title']
            print(origin_book)

            # НЕ ОЧЕНЬ АКТУАЛЬНО
            # предусмотреть выбор автора здесь <----->
            # 1) парсинг всех авторов
            # 2) добавление их в список
            # 3) вывод авторов со списка в кнопки телеграм
            # 4) после нажатия на кнопку выбранного автора, его имя отправляется в чат
            # П.С. данный выбор только для сайта лабиринт. Если выбирать для всех 3х сайтов, будет не очень красиво

            # если в тексте нет -, то значит нет автора
            if '-' not in origin_book:
                # поэтому название книги равно автор
                author = book = origin_book
            else:
                # достаю название автора
                author = origin_book.split('-')[0]
                # достаю название книги
                book = origin_book.split('-')[1][1:]
            # минимальная цена для сравнения
            min_price = 9999999
            # самая дешевая книга на сайте
            cheap_book = {}

            # перебор по всем карточкам книг на странице
            for i in soup:
                # нахожу полное название книги, которое имеет вид: автор - название книги
                full_name = i.find('a', attrs={'class': 'cover'})['title']
                # если есть необходимый автор в названии книги
                if author in full_name:
                    # и если это та книга, которая нужна
                    if book in full_name:
                        # достаю цену
                        price = i.find('span', attrs={'class': 'price-val'}).text
                        # тк она достается с переносом строки и знаком рубля, то сначала убираю знак рубля и ненужные пробелы, затем
                        # перевожу в инт, чтобы убрались переходы строки
                        price = int(price.replace(' ', '').replace('₽', ''))
                        # если цена меньше минимальной
                        if price < min_price:
                            min_price = price
                        else:
                            continue
                        # достаю ссылку на книгу
                        link = 'https://www.labirint.ru' + str(
                            i.find('a', attrs={'class': 'product-title-link'})['href'])
                        # достаю картинку
                        image = i.find('a', attrs={'class': 'cover'}).find('img').get('src')


                        # добавляю либо перезаписываю
                        cheap_book['name'] = full_name
                        cheap_book['price'] = price
                        cheap_book['link'] = link
                        cheap_book['image'] = image
                    else:
                        pass
                else:
                    pass
            # возвращаю словарь с самой дешевой книгой
            return cheap_book

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
