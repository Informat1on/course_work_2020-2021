import requests
from bs4 import BeautifulSoup

def main(request):
    cheap_book = {}
    min_price = 999999
    source = requests.get(f'https://fitabooks.ru/?s={request}&post_type=product&title=1&excerpt=1&content=1&categories=1&attributes=1&tags=1&sku=1&orderby=date-DESC&ixwps=1').text
    soup = BeautifulSoup(source,'lxml')

    try:
        # пытаюсь получить айтемы
        items = soup.find_all('li',class_='product')
        for item in items:
            name = item.find('h2').text
            # проверяю на название
            # если в названии есть требуемый запрос то идем дальше по циклу
            if (name.upper().startswith(request.upper()) or name.upper().endswith(request.upper())):
                price = int(item.find_all('bdi')[1].text.split('\xa0')[0])
                # тк мы ищем минимальную цену, то сравниваем
                if (price < min_price):
                    min_price = price
                    link = item.find('a').get('href')
                    image = item.find('img').get('src')

                    # добавляю в словарь
                    cheap_book['name'] = name
                    cheap_book['price'] = price
                    cheap_book['link'] = link
                    cheap_book['image'] = image
                else:
                    continue
            else:
                pass
    except Exception as e:
        # иначе даем понять, что проверять не нужно
        cheap_book['price'] = None
        print(e)


    return cheap_book