import requests
from bs4 import BeautifulSoup

def main(request):
    cheap_book = {}
    min_price = 9999999

    source = requests.get(f'https://polka23.ru/?s={request}').text
    soup = BeautifulSoup(source,'lxml')

    try:
        # нахожу все карточки продукта
        items = soup.find_all('div',class_='one oneitem')
        # получаю фамилию автора, чтобы отсеять ненужные книги
        book_author = soup.find('div',class_='author').text.split(' ')[0]

        # делаю перебор
        for item in items:
            # может автора и не быть, поэтому отсеиваю exceptом ненеужное
            try:
                author = item.find('div',class_='author').text
                # если это тот автор, то
                if (author.upper().startswith(book_author.upper()) or author.upper().endswith(book_author.upper())):
                    price = int(item.find('span',class_='noredPrice').text.split(' ')[0])
                    if (price < min_price):
                        min_price = price
                        # получаю нужные данные
                        name = item.find('span').text
                        link = item.find('a').get('href')
                        image = item.find('img').get('src')

                        # добавляю в словарь
                        cheap_book['name'] = name
                        cheap_book['price'] = price
                        cheap_book['link'] = link
                        cheap_book['image'] = image
                else:
                    continue

            except:
                continue

    # если все неудачно
    except:
        cheap_book['price'] = None

    return cheap_book