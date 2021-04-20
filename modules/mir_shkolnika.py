import requests
from bs4 import BeautifulSoup

def main(request):
    cheap_book = {}
    min_price = 9999999

    source = requests.get(f'http://www.uchebnik.com/katalog/?items_per_page=100&filter%5Bsearch%5D={request}').text
    soup = BeautifulSoup(source,'lxml')

    try:
        # нахожу все элементы
        items = soup.find_all('div',class_='tovar tile')
        # делаю перебор каждого
        for item in items:
            # достаю цену
            price = item.find_all('span',class_='item_price')
            # если она со скидкой, то кладу в пееременную цену со скидкой
            if (len(price) > 1):
                price = int(price[1].text)
            # если скидки нет
            else:
                price = int(price[0].text)

            # если цена меньше минимальной
            if (price < min_price):
                min_price = price
                # достаю нужные данные
                name = item.find('span', class_='name_tovar').text
                link = 'http://www.uchebnik.com' + item.find('a').get('href')
                image = 'http://www.uchebnik.com' + item.find('img').get('src')

                # добавляю в словарь
                cheap_book['name'] = name
                cheap_book['price'] = price
                cheap_book['link'] = link
                cheap_book['image'] = image

            else:
                continue
    # если случилось что то - печатаем ошибку
    except Exception as e:
        cheap_book['price'] = None
        print(f'[Mir-shkolnika Exception]: {e}')

    return cheap_book