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
        print("[INFO] Проверка на наличие таблицы с командами.")
        if tag != None:
            return True
        else:
            return False

    def check_for_n_matches(self, tag):
        print("[INFO] Проверка количества матчей в таблице Results.")
        if(len(tag)) < self.number_of_history_matches:
            return True

    def find_matches(self, html): #Поиск 10 предыдущих матчей команды
        history_matches = []
        soup = BeautifulSoup(html, 'lxml')
        table_with_matches = soup.find('table', class_='table-main')
        rows = table_with_matches.find_all(self.check_empty_table)
        if self.check_for_n_matches(rows):
            return False
        else:
            for i in range(0, self.number_of_history_matches):
                match_time_td = rows[i].find('td', class_='table-time')
                match_time = match_time_td['class'][2][1:11]
                match_link = rows[i].find('td', class_='name table-participant').a.get('href')
                history_matches.append({
                    'Time': match_time,
                    'Link': self.base_url + match_link
                    })
        return history_matches

    def find_table_of_history_matches(self, team_url, team_sport, team_country, team_name):
        teams = []
        history_matches = []
        soup = BeautifulSoup(self.get_page(team_url), 'lxml')
        table_with_teams = soup.find('table', class_='sortable table-main')
        if self.check_tables_for_teams(table_with_teams):
            rows = table_with_teams.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                teams.append({
                    'Team': cols[0].get_text().strip(),
                    'Link': cols[0].a.get('href').strip(),
                    'Country': cols[2].get_text().strip(),
                    'Sport': cols[1].get_text().strip(),
                    })
            for team in teams:
                if team['Team'] == team_name and team['Country'] == team_country and team['Sport'] == team_sport:
                    history_matches = self.find_matches(self.get_page(self.base_url + team['Link']))
                    break
                else:
                    raise Exception('No history matches for team:', team_name)
        else:
            history_matches = self.find_matches(self.get_page(team_url))
        return history_matches

    def print_history_matches(self, matches_home_team, matches_guest_team):
        for i in range(0, self.number_of_history_matches):
            self.matches_home_team[i].short_show_match2()
            print(' ', end = '')
            self.matches_guest_team[i].short_show_match2()
            print('\n')

    def run(self):
        match_node = Match(self.match_url)
        match_node.run()
        match_node.show_match()
        matches_home_team = self.find_table_of_history_matches(match_node.team_home_url,
                                                               match_node.sport,
                                                               match_node.country,
                                                               match_node.team_home)
        print(matches_home_team)
        matches_guest_team = self.find_table_of_history_matches(match_node.team_guest_url,
                                                                match_node.sport,
                                                                match_node.country,
                                                                match_node.team_guest)

        if (matches_home_team is not False) & (matches_guest_team is not False):
            pass
        else:
            print("[ERROR] Не найдено", number_of_history_matches, "матчей в таблице Results у одной из команд.")


def main():
    start_time = time()
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-n", "--number", default=5)
    args = vars(arg_parser.parse_args())
    number_of_history_matches = int(args["number"])

    print("[INFO] Количество матчей из истории:", number_of_history_matches)

    match_url = input('[INFO] Введите URL матча: ')

    process = Process(number_of_history_matches, match_url)
    process.run()

    end_time = time() - start_time
    print('[INFO] Программа завершена за: ', end_time/60, ' мин.')
    #try:
    #    print('Finnaly:')
    #    print_history_matches(matches_home_team, matches_guest_team)
    #except Exception as err:
    #    print('[ERROR]', err.args[0])

if __name__ == '__main__':
    main()
    input("Press Enter to continue...")
