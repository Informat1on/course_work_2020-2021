import requests
from bs4 import BeautifulSoup

def main(book_name):
    cheap_book = {}
    all_books = []

    headers = {
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }
    book_name_edited = book_name.replace(' ', '%20')
    source = requests.get(f'https://www.labirint.ru/search/{book_name_edited}/'
                          f'?stype=0&available=1&preorder=1&paperbooks=1', headers = headers).text
    soup = BeautifulSoup(source, 'lxml')

    # пытаюсь найти ошибку в поиске
    try:
        h1 = soup.find('div', attrs={'class': 'search-error'}).find('h1').text
        return None

    # если ошибок нет
    except:
        soup = soup.find_all('div', attrs={'class': 'card-column'})

        try:
            # выбираем самую первую книгу, тк это 100% совпадение
            # и берем с этой книги название + автора отдельно, чтобы отсеять всякие рецензии и прочее ненужное
            origin_book = soup[0].find('a', attrs={'class': 'cover'})['title']

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

            # перебор по всем карточкам книг на странице
            for i in soup:
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

                        # достаю ссылку на книгу
                        link = 'https://www.labirint.ru' + str(
                            i.find('a', attrs={'class': 'product-title-link'})['href'])
                        # достаю картинку
                        image = i.find('a', attrs={'class': 'cover'}).find('img').get('src')
                        if (image == 'https://img.labirint.ru/design/emptycover-big.svg'):
                            image = 'https://www.allianceplast.com/wp-content/uploads/2017/11/no-image.png'
                        else:
                            pass

                        # добавляю все книги в определенный массив
                        all_books.append({'name': full_name, 'price': price, 'link': link, 'image': image})

                        # если цена меньше минимальной
                        if price < min_price:
                            min_price = price
                        else:
                            continue

                        # добавляю либо перезаписываю
                        cheap_book['name'] = full_name
                        cheap_book['price'] = price
                        cheap_book['link'] = link
                        cheap_book['image'] = image
                    else:
                        pass
                else:
                    pass
        except Exception as e:
            cheap_book['price'] = None
            print(f'[Labirint Exception]: {e}')
            # значит требуемой книги нет в наличии
            # return None
        # возвращаю словарь с самой дешевой книгой
    return cheap_book,all_books