import requests
from bs4 import BeautifulSoup

string  = u'Муму'
string.encode('Windows-1251').decode('utf-8'
)
print(string)

def main(request):
    cheap_book = {}
    min_price = 9999999

    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 5.0.2; SAMSUNG SM-T550 Build/LRX22G) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/3.3 Chrome/38.0.2125.102 Safari/537.36'
    }

    source = requests.get(f'https://www.combook.ru/search/?search_str={request}&onpg=500',headers=headers).text
    soup = BeautifulSoup(source,'lxml')

    try:
        items = soup.find('ul',class_='grid').find_all('li')

        for item in items:
            try:
                # пытаюсь найти книги в наличии
                try:
                    # если есть кнопка предзаказ - книга oos
                    button = item.find('a',class_='predzakaz predzakaz_button').text
                    continue
                except:
                    # иначе в наличии
                    pass


                price = int(float(item.find('div',class_='price').get('product_price')))

                if (price < min_price):
                    min_price  = price

                    link = 'https://www.combook.ru' + item.find('a').get('href')
                    name = item.find('img').get('title')
                    image = 'https://www.combook.ru' + item.find('img').get('src')

                    cheap_book['name'] = name
                    cheap_book['price'] = price
                    cheap_book['link'] = link
                    cheap_book['image'] = image
                else:
                    pass
            except:
                price = 999999
    except Exception as e:
        print(e)
        cheap_book['price'] = None


    return cheap_book