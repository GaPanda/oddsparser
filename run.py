#-*- coding: utf-8 -*-

from time import time
from urllib.request import urlopen
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from modules.clmatch import Match

class Process:
    def __init__(self, number_of_history_matches, match_url):
        super(Process, self).__init__()
        self.match_url = match_url
        self.number_of_history_matches = number_of_history_matches
        self.base_url = 'http://www.oddsportal.com'
        self.matches_home_team = []
        self.matches_guest_team = []

    def get_page(self, url):
        page = urlopen(url)
        return page.read()

    def check_empty_table(self, tag):
        return tag.has_attr('class') and tag.has_attr('xeid') and tag.name == 'tr'

    def check_tables_for_teams(self, tag): #Проверка на наличие таблицы с командами
        print("[INFO] Проверка на наличие таблицы с матчами.")
        if tag != None: return True
        else: return False

    def check_for_n_matches(self, tag, page):
        print("[INFO] Поиск матчей в истории на странице {}.".format(page))
        if(len(tag)) > self.number_of_history_matches: return True

    def find_matches(self, url, node_time, array): #Поиск 10 предыдущих матчей команды
        html = self.get_page(url)
        soup = BeautifulSoup(html, 'lxml')
        div_pagination = soup.find('div', id="pagination")
        last_page = int(div_pagination.find_all('a')[-1].get('x-page'))
        added_matches = 0
        page = 1
        while((added_matches < self.number_of_history_matches) & (page <= last_page)):
            html = self.get_page(url + '/page/' + str(page))
            soup = BeautifulSoup(html, 'lxml')
            table_with_matches = soup.find('table', class_='table-main')
            rows = table_with_matches.find_all(self.check_empty_table)
            if self.check_for_n_matches(rows, page):
                for row in rows:
                    match_time_td = row.find('td', class_='table-time')
                    match_time = int(match_time_td['class'][2][1:11])
                    match_link = row.find('td', class_='name table-participant').a.get('href')
                    if (node_time > match_time) & (added_matches < self.number_of_history_matches):
                        node = Match(self.base_url + match_link)
                        array.append(node)
                        added_matches += 1
                        node.start()
            else: raise ValueError
            page += 1

    def count_teams(self, teams, name, sport):
        count_similar = 0
        for team in teams:
            if team['name'] == name and team['sport'] == sport:
                count_similar += 1
        return count_similar

    def find_table_of_history_matches(self, url, sport, country, name, node_time, array):
        teams = []
        soup = BeautifulSoup(self.get_page(url), 'lxml')
        table_with_teams = soup.find('table', class_='sortable table-main')
        if self.check_tables_for_teams(table_with_teams):
            rows = table_with_teams.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                teams.append({
                    'name': cols[0].get_text().strip(),
                    'link': cols[0].a.get('href').strip(),
                    'country': cols[2].get_text().strip(),
                    'sport': cols[1].get_text().strip(),
                    })
            num = self.count_teams(teams, name, sport)
            if num == 1:
                self.find_matches(self.base_url + teams[0]['link'], node_time, array)
            elif num > 1:
                for team in teams:
                    if team['name'] == name and team['sport'] == sport and team['country'] == country:
                        self.find_matches(self.base_url + team['link'], node_time, array)
                        break
            else: raise ValueError
        else: self.find_matches(url, node_time, array)

    def print_history_matches(self):
        i = 1
        print(u'\n--------------Матчи домашней команды-------------')
        for key in self.matches_home_team:
            print(u'\nМатч №{}'.format(i))
            key.show_match()
            i += 1
        print('\n--------------Матчи гостевой команды-------------')
        i = 1
        for key in self.matches_guest_team:
            print(u'\nМатч №{}'.format(i))
            key.show_match()
            i += 1

    def join_threads(self):
        for key in self.matches_home_team:
            key.join()
        for key in self.matches_guest_team:
            key.join()

    def run(self):
            match_node = Match(self.match_url)
        #try:
            match_node.run()
            match_node.show_match()
            if match_node.sport == "Basketball":
                self.find_table_of_history_matches(match_node.team_home_url,
                                                   match_node.sport,
                                                   match_node.country,
                                                   match_node.team_home,
                                                   match_node.match_time,
                                                   self.matches_home_team)
                self.find_table_of_history_matches(match_node.team_guest_url,
                                                   match_node.sport,
                                                   match_node.country,
                                                   match_node.team_guest,
                                                   match_node.match_time,
                                                   self.matches_guest_team)
                self.join_threads()
                if (len(self.matches_home_team) != 0) & (len(self.matches_guest_team) != 0):
                    self.print_history_matches()
                else:
                    print("[ERROR] Не найдено матчей у одной из команд.")
            else:
                print("[WARNING] Пока что только баскетбол :(")
        #except Exception as err:
        #    print('[ERROR] Что-то пошло не так', err)

def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-n", "--number", default=5)
    args = vars(arg_parser.parse_args())
    number_of_history_matches = int(args["number"])
    print("[INFO] Количество матчей из истории:", number_of_history_matches)
    match_url = input('[INFO] Введите URL матча: ')
    start_time = time()
    process = Process(number_of_history_matches, match_url)
    process.run()
    end_time = time() - start_time
    print('[INFO] Программа завершена за: {0:.2f} секунд.'.format(end_time))

if __name__ == '__main__':
    main()
    input("Press Enter to continue...")
