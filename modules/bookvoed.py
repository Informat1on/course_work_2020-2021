import requests
from bs4 import BeautifulSoup

def main(request):
    source = requests.get(f'https://www.bookvoed.ru/books?q={request}').text
    soup = BeautifulSoup(source,'lxml')

    print(soup)

main('Муму')