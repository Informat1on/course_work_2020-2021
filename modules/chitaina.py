import requests
from bs4 import BeautifulSoup

def main(request):
    cheap_book = {}
    min_price = 999999

    source = requests.get(f'https://chitaina.ru/search/result?setsearchdata=1&category_id=&include_subcat=1&xs_categories=&search_type=all&search={request}').text
    soup = BeautifulSoup(source,'lxml')

    try:
        # нахожу имя автора, чтобы отсеять ненужные книги
        book_author = soup.find('div',class_='shell').find('span',class_='designation').find('span').text.split(' ')[0]
        # нахожу все  карточки товаров
        items = soup.find_all('div',class_='shell')
        # делаю перебор элементов
        for item in items:
            # пытаюсь найти автора книги
            try:
                author = item.find('span',class_='designation').find('span').text
            # если такого нет, то пропускаю
            except:
                continue
            # если автор нужный
            if (author.upper().startswith(book_author.upper()) or author.upper().endswith(book_author.upper())):
                try:
                    price1  = item.find('span', class_='numbers').find('strong').text
                    price = int(price1[:price1.find(' р.')].replace('₽','').replace(' ',''))
                    # price = int(item.find('span', class_='numbers').find('strong').text.split(' ')[0])
                except AttributeError:
                    price1 = item.find('span', class_='numbers').text
                    price = int(price1[:price1.find(' р.')].replace('₽','').replace(' ',''))
                    # price = int(item.find('span', class_='numbers').text.split(' ')[0])
                # если цена меньше минимальной
                if (price < min_price):
                    min_price = price
                    # достаю нужные данные
                    name = item.find('strong').text
                    link = 'https://chitaina.ru' + item.find('a').get('href')
                    image = item.find('img').get('src')

                    # добавляю в словарь
                    cheap_book['name'] = name
                    cheap_book['price'] = price
                    cheap_book['link'] = link
                    cheap_book['image'] = image

                else:
                    continue
            else:
                continue
    # если случилось что то - печатаем ошибку
    except Exception as e:
        cheap_book['price'] = None
        print(f'[Chitaina Exception]: {e}')

    return cheap_book