import requests
from bs4 import BeautifulSoup

request = 'муму'
source = requests.get(f'https://fkniga.ru/search/?q={request}&category=2721&page-size=2048').text
soup  =  BeautifulSoup(source,'lxml')

items = soup.find_all('div',class_='grid__item columnDesktop--3 columnSmallDesktop--4 columnTablet--4 columnMobile--12')

for i in items:
    name = i .find('a',class_='card__title').text
    if (name.startswith(request.capitalize()) or name.endswith(request.capitalize())):
        print(name)
