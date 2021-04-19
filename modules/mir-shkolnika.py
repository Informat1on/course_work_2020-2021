import requests
from bs4 import BeautifulSoup

def main(request):
    source = requests.get(f'http://www.uchebnik.com/katalog/?filter%5Bsearch%5D={request}').text
    soup = BeautifulSoup(source,'lxml')

    print(soup)

main('муму')