import requests
from bs4 import BeautifulSoup

def main(request):
    source = requests.get(f'https://fkniga.ru/search/?q={request}&category=2721&page-size=2048').text
    soup = BeautifulSoup(source,'lxml')

    cheap_book = {}
    # ставлю максимальную цену, чтобы дальше сравнивать
    min_price = 99999999

    # если удается получить данные с сайта
    try:
        #получаю все карточки с книгами
        items = soup.find_all('div',class_='grid__item columnDesktop--3 columnSmallDesktop--4 columnTablet--4 columnMobile--12')

        # делаю перебор карточек
        for i in items:
            # получаю название книги
            name = i .find('a',class_='card__title').text
            # если в названии находится требуемый запрос
            keywords = [request, request.lower(), request.upper()]
            for keyword in keywords:
                if (keyword in name and ('Плакат' not in name and 'плакат' not in name and 'Обложка' not in name and 'обложка' not in name)):
                    # далее находим самую дешевую
                    price = int(i.find('div',class_='price price--ruble').text.replace(' ',''))
                    if (price < min_price):

                        link = 'https://fkniga.ru' + i.find('div', class_='card__body').find('a').get('href')
                        try:
                            image = 'https://fkniga.ru' + i.find('div', class_='card__photo').find('img').get('src')
                        except:
                            image = 'https://www.allianceplast.com/wp-content/uploads/2017/11/no-image.png'

                        cheap_book['name'] = name
                        cheap_book['price'] = price
                        cheap_book['link'] = link
                        cheap_book['image'] = image
                    else:
                        continue
                else:
                    continue

    # если не удается - даем сигнал о том, что не нужно проверять эту переменную
    except Exception as e:
        cheap_book['price'] = None
        print(f'[Fkniga Exception]: {e}')

    return cheap_book