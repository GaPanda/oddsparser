# -*- coding: utf-8 -*-

from threading import Thread
from urllib.request import urlopen
from bs4 import BeautifulSoup


def get_page(url):
    page = urlopen(url)
    return page.read()


class HistoryMatches(Thread):
    def __init__(self, number_of_history_matches, sport, country, name, node_time):
        super(HistoryMatches, self).__init__()
        self.base_url = 'http://www.oddsportal.com'
        self.sport = sport
        self.country = country
        self.name = name
        self.node_time = node_time
        self.matches_urls = []
        self.number_of_history_matches = number_of_history_matches

    def create_url(self, team_name, sport):
        '''Создание URL ссылки из названия клуба'''
        url = 'http://www.oddsportal.com/search/results/'
        typesport = '/' + sport + '/'
        split_team_name = team_name.split()
        url_team_name = url + '%20'.join(split_team_name) + typesport.lower()
        return url_team_name

    def check_empty_table(self, tag):
        return tag.has_attr('class') and tag.has_attr('xeid') and tag.name == 'tr'

    def check_tables_for_teams(self, tag):
        '''Проверка на наличие таблицы с командами'''
        print("[INFO] Проверка на наличие таблицы с матчами.")
        if tag is not None:
            return True
        else:
            return False

    def check_for_n_matches(self, tag, page):
        print("[INFO] Поиск матчей в истории на странице {}.".format(page))
        if(len(tag)) > self.number_of_history_matches:
            return True

    def find_matches(self, url, node_time):
        '''Поиск 10 предыдущих матчей команды'''
        html = get_page(url)
        soup = BeautifulSoup(html, 'lxml')
        div_pagination = soup.find('div', id="pagination")
        if div_pagination is not None:
            last_page = int(div_pagination.find_all('a')[-1].get('x-page'))
        else:
            last_page = 1
        added_matches = 0
        page = 1
        while((added_matches < self.number_of_history_matches) & (page <= last_page)):
            html = get_page(url + '/page/' + str(page))
            soup = BeautifulSoup(html, 'lxml')
            table_with_matches = soup.find('table', class_='table-main')
            rows = table_with_matches.find_all(self.check_empty_table)
            if self.check_for_n_matches(rows, page):
                for row in rows:
                    match_time_td = row.find('td', class_='table-time')
                    match_time = int(match_time_td['class'][2][1:11])
                    match_link = row.find('td', class_='name table-participant').a.get('href')
                    if (node_time > match_time) & (added_matches < self.number_of_history_matches):
                        node = self.base_url + match_link
                        self.matches_urls.append(node)
                        added_matches += 1
            else:
                break
            page += 1

    def count_teams(self, teams, name, sport):
        count_similar = 0
        for team in teams:
            if team['name'] == name and team['sport'] == sport:
                count_similar += 1
        return count_similar

    def run(self):
        teams = []
        url = self.create_url(self.name, self.sport)
        soup = BeautifulSoup(get_page(url), 'lxml')
        table_with_teams = soup.find('table', class_='sortable table-main')
        if self.check_tables_for_teams(table_with_teams):
            rows = table_with_teams.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                teams.append({'name': cols[0].get_text().strip(),
                              'link': cols[0].a.get('href').strip(),
                              'country': cols[2].get_text().strip(),
                              'sport': cols[1].get_text().strip(),
                              })
            num = self.count_teams(teams, self.name, self.sport)
            if num == 1:
                self.find_matches(self.base_url + teams[0]['link'], self.node_time)
            elif num > 1:
                for team in teams:
                    if team['name'] == self.name and team['sport'] == self.sport and team['country'] == self.country:
                        self.find_matches(self.base_url + team['link'], self.node_time)
                        break
            else:
                raise ValueError
        else:
            self.find_matches(url, self.node_time)
