import requests
from bs4 import BeautifulSoup

request = 'муму'
source = requests.get(f'https://fkniga.ru/search/?q={request}&category=2721&page-size=2048').text
soup  =  BeautifulSoup(source,'lxml')

#получаю все карточки с книгами
items = soup.find_all('div',class_='grid__item columnDesktop--3 columnSmallDesktop--4 columnTablet--4 columnMobile--12')

# делаю перебор карточек
for i in items:
    # получаю название книги
    name = i .find('a',class_='card__title').text
    # если в названии находится требуемый запрос
    if (name.startswith(request.capitalize()) or name.endswith(request.capitalize())):
        print(name)
