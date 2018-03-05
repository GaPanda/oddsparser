from urllib.request import urlopen
from bs4 import BeautifulSoup

URL = "http://www.oddsportal.com"

def get_html(url):
    request = urlopen(url)
    return request.read()

def parse_sports(): #Парсинг ссылок для лиг
    sports = []
    html = get_html(URL)
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('ul', id = 'sports-menu')
    li = table.find_all('li', class_ = 'sport')
    for key in li:
        sport = key.find('a').get_text()
        sport_link = key.find('a').get('href')
        full_sport_link = URL + sport_link
        sports.append(Sport(sport, full_sport_link))
    return sports

class League:
    def __init__(self, league_name, country_name, league_url):
        self.league_name = league_name
        self.league_url = league_url
        self.country_name = country_name
        self.matches_urls = []

    def check_tag_match(self, tag):
        return tag.has_attr('xeid') and tag.name == 'tr'

    def parse_league(self):
        html = get_html(self.league_url)
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find('table', class_=" table-main")
        try:
            tbody = table.find('tbody')
            tr = tbody.find_all(self.check_tag_match)
            for tr_tag in tr:
                td = tr_tag.find('td', class_ = 'name table-participant')
                a = td.find_all('a')
                match_url = a[-1].get('href').strip()
                self.matches_urls.append(URL + match_url)
        except:
            pass

    def print_league(self):
        print('League name:', self.league_name)
        print('Country:', self.country_name)
        print('League URL:', self.league_url)
        for match_url in self.matches_urls:
            print(match_url)

class Sport:
    def __init__(self, sport_name, sport_url):
        self.sport_name = sport_name
        self.sport_url = sport_url
        self.leagues = []

    def check_tag_country(self, tag):
        return tag.has_attr('class') and tag.name == 'tr'

    def check_tag_league(self, tag):
        return tag.has_attr('xtid') and tag.name == 'td'

    def parse_sport(self):
        html = get_html(self.sport_url)
        soup = BeautifulSoup(html, 'lxml')
        tbody = soup.find('tbody')
        tr = tbody.find_all(self.check_tag_country)
        country_name = None
        for tr_tag in tr:
            if tr_tag['class'][0] == 'center':
                a_tr = tr_tag.find('a')
                country_name = a_tr.get_text().strip()
            elif tr_tag['class'][0] == 'odd':
                td = tr_tag.find_all(self.check_tag_league)
                for td_tag in td:
                    a_td = td_tag.find('a')
                    league_name = a_td.get_text().strip()
                    league_url = URL + a_td.get('href').strip()
                    self.leagues.append(League(league_name, country_name, league_url))

    def parse_leagues(self):
        print('Sport:', self.sport_name)
        for league in self.leagues:
            league.parse_league()
            league.print_league()
            print('------------------------------')

    def count_matches(self):
        sum_matches = 0
        for league in self.leagues:
            sum_matches += len(league.matches_urls)
        print('Всего найдено матчей:', sum_matches)

def start():
    sports = parse_sports()
    for sport in sports:
        if sport.sport_name == "Basketball":
            sport.parse_sport()
            sport.parse_leagues()
            sport.count_matches()

if __name__ == '__main__':
    start()
