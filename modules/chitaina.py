import requests
from bs4 import BeautifulSoup

def main(request):
    cheap_book = {}
    min_price = 999999

    source = requests.get(f'https://chitaina.ru/search/result?setsearchdata=1&category_id=&include_subcat=1&xs_categories=&search_type=all&search={request}').text
    soup = BeautifulSoup(source,'lxml')

    items = soup.find_all('div',class_='shell')
    for item in items:
        name = item.find('strong').text
        print(name)

main('Муму')