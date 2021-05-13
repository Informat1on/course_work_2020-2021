import requests
from bs4 import BeautifulSoup

def main(request):
    cheap_book = {}
    min_price = 999999

    source = requests.get(f'https://www.bookvoed.ru/books?q={request}&ishop=true&in_shop=true&pod=true&desc=1&order=relevancy&lang=rus').text
    soup = BeautifulSoup(source,'lxml')

    try:
        items = soup.find_all('div',class_='Zg')
        # тк 1 запрос самый точный, сохраняем фамилию автора для сравнения
    #     book_author = soup.find('div', class_='fq').text.split(' ')[0].replace(' ','').replace('\n','')
    #
    #   перебираю каждую карточку продукта
        keywords = [request, request.lower(), request.upper()]
        for item in items:
            name = item.find('a', class_='eq').text.replace('  ', '').replace('\n', '')
            for keyword in keywords:
                if (keyword in name and ( 'Плакат' not in name and 'плакат' not in name and 'Обложка' not in name and 'обложка' not in name and
                                          'стикер' not in name)):
    #         author = item.find('div', class_='fq').text.replace('  ','').replace('\n','')
    #         # если это нужный автор
    #         if (author.upper().startswith(book_author.upper()) or author.upper().endswith(book_author.upper())):
                # пытаюсь получить цену, если ее нет, то товара нет в наличии
                    try:
                        price1 = item.find('div',class_='iq').text
                        price = int(price1[:price1.find('руб.')].replace('₽','').replace(' ',''))
                    except:
                        continue

                    # ищу самый дешевый товар
                    if (price < min_price):
                        min_price = price
                        # получаю имя, ссылку, картину
                        name = item.find('a',class_='eq').text.replace('  ','').replace('\n','')
                        link = item.find('a',class_='eq').get('href')
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
        print(f'[Bookvoed Exception]: {e}')

    return cheap_book