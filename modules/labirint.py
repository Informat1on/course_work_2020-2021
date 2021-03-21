import requests
from bs4 import BeautifulSoup
from selenium import webdriver

def main(book_name):
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

main('Мастер и  маргарита')
print('none')