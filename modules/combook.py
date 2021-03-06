import requests
from bs4 import BeautifulSoup

def main(string):
    word = string.encode('cp1251')
    request = ''
    # нужно перевести в hex
    for i in word:
        hexy = hex(i).lstrip("0x").rstrip("L").upper()
        request += '%' + hexy

    cheap_book = {}
    all_books = []
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

                name = item.find('img').get('title').replace('\n','').replace('  ','')
                # name = item.find('span',class_='name').find('span').text
                keywords = [string, string.lower(), string.upper()]
                for keyword in keywords:
                    if (keyword in name and ('Плакат' not in name and 'плакат' not in name and 'Обложка' not in name and 'обложка' not in name )):
                        price = int(float(item.find('div',class_='price').get('product_price')))
                        link = 'https://www.combook.ru' + item.find('a').get('href')
                        image = 'https://www.combook.ru' + item.find('img').get('src')

                        # добавляю все книги в определенный массив
                        all_books.append({'name': name, 'price': price, 'link': link, 'image': image})

                        if (price < min_price):
                            min_price = price

                            cheap_book['name'] = name
                            cheap_book['price'] = price
                            cheap_book['link'] = link
                            cheap_book['image'] = image
                        else:
                            pass
                    else:
                        continue
            except:
                continue
    except Exception as e:
        print(f'[Combook Exception]: {e}')
        cheap_book['price'] = None


    return cheap_book,all_books