from selenium import webdriver
from bs4 import BeautifulSoup
import time

def main(book_name):
    book_name = book_name.replace(' ', '%20')
    browser = webdriver.Chrome()
    try:
        browser.get(f'https://www.m.chitai-gorod.ru/search/result/?q={book_name}')
        time.sleep(10)
        source = browser.page_source
        # нужно предварительно написать pip install bs4 и lxml
        soup = BeautifulSoup(source, 'lxml')

        # так как страниц несколько, то нужно пробежаться по всем им
        # количество страниц
        pages = soup.find_all('a', attrs={'class': 'pagination-item js__pagination_item'})
        pages = len(pages)

        soup = soup.find_all('div', attrs={'class': 'product-card js_product js__product_card'})
        print('Ищу книги')

        # автор и название книги - 1 выведенная книга в поиске, тк поиск на 100% точный
        book = soup[0].find('div', attrs={'class': 'product-card__title js-analytic-product-title'}).text
        author = soup[0].find('div', attrs={'class': 'product-card__author'}).text

        # минимальная цена книги
        min_price = 9999999
        # словарь для хранения данных о самой дешевой книге
        cheap_book = {}
        for index in range(0, pages):
            browser.get(f'https://www.chitai-gorod.ru/search/result/?q={book_name}&page={index + 1}')
            source = browser.page_source
            time.sleep(10)
            soup = BeautifulSoup(source, 'lxml')
            soup = soup.find_all('div', attrs={'class': 'product-card js_product js__product_card'})

            for i in range(len(soup)):
                print(f'page is {index} and item is {i}')
                try:
                    curr_book = soup[i].find('div',
                                             attrs={'class': 'product-card__title js-analytic-product-title'}).text
                    # ошибка возникает на авторе
                    curr_author = soup[i].find('div', attrs={'class': 'product-card__author'}).text
                except:
                    continue

                # если это нужный автор и книга
                if author in curr_author:
                    if book in curr_book:
                        # если есть возможность купить
                        try:
                            if ('Купить' in soup[i].find('span', attrs={'class': 'js__card_button_text'}).text) or (
                                    'купить' in soup[i].find('span', attrs={'class': 'js__card_button_text'}).text):

                                # достаю цену
                                try:
                                    price = int(soup[i].find('span', attrs={'class': 'price'}).text.split(' ')[0])
                                except:

                                    continue
                                # если цена меньше минимальной, то теперь минимальная цена - цена этого товара
                                if price < min_price:
                                    min_price = price
                                else:
                                    continue
                                cheap_book['name'] = f'{author} - {book}'
                                cheap_book[
                                    'link'] = f"https://www.chitai-gorod.ru{soup[i].find('a', attrs={'class': 'product-card__link js-watch-productlink'})['href']}"
                                cheap_book['price'] = price
                                cheap_book['image'] = f"{soup[i].find('img')['data-src']}"
                        except:
                            pass

                            print(
                                f"{author} - {book} # price is {min_price} #link is {cheap_book['link']} # image is {cheap_book['image']}")
        browser.close()
        return cheap_book
    except:
        return None

print(main('Мастер и маргарита'))