import requests
from bs4 import BeautifulSoup

def main(request):
    cheap_book = {}
    min_price = 999999

    source = requests.get(f'https://www.bookvoed.ru/books?q={request}&ishop=true&in_shop=true&pod=true&desc=1&order=relevancy').text
    soup = BeautifulSoup(source,'lxml')

    try:
        items = soup.find_all('div',class_='Zg')
        # тк 1 запрос самый точный, сохраняем фамилию автора для сравнения
        book_author = soup.find('div', class_='fq').text.split(' ')[0]

    #   перебираю каждую карточку продукта
        for item in items:
            author = item.find('div', class_='fq').text
            # если это нужный автор
            if (author.upper().startswith(book_author.upper()) or author.upper().endswith(book_author.upper())):
                # пытаюсь получить цену, если ее нет, то товара нет в наличии
                try:
                    price = int(item.find('div',class_='iq').text.split()[0])
                except:
                    continue

                # ищу самый дешевый товар
                if (price < min_price):
                    min_price = price
                    # получаю имя, ссылку, картину
                    name = item.find('a',class_='vIb eq').text
                    link = item.find('a',class_='vIb eq').get('href')
                    image = 'https://www.bookvoed.ru' + item.find('img').get('src')

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
        print(e)

    return cheap_book