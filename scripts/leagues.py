from urllib.request import urlopen
from bs4 import BeautifulSoup

URL = "http://www.oddsportal.com/site-map-active/"

def get_html(url):
    request = urlopen(url)
    return request.read()

class League:
    def __init__(self, league_name, tag):
        self.league_name = league_name
        self.matches_urls = []

class Country:
    def __init__(self, country_name, tag):
        self.country_name = country_name
        self.leagues_urls = []

class Sport:
    def __init__(self, sport_name, tag):
        self.sport_name = sport_name
        self.countries_urls = []

def main():
    html = get_html(URL)
    soup = BeautifulSoup(html, 'lxml')
    site_map = soup.find('div', id='site-map-active')
    print(site_map)

    #li = site_map.find_all('li', recursive = False)

if __name__ == '__main__':
    main()
