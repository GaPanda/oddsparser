#-*- coding: utf-8 -*-

import pickle
from time import time
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from modules.clmatch import get_page
from modules.clmatch import Match
from modules.clratio import MatchRatio

class Process:
    def __init__(self, arg):
        super(Process, self).__init__()
        self.BASE_URL = 'http://www.oddsportal.com'


BASE_URL =

    def try_to_connect(self):
        try:
            self.open_connection()
            self.logging_in(self.login, self.passw)
            print("[INFO] Успешный вход!")
        except Exception as err:
            print("[WARNING]", err.args[0])

    def open_connection(self):
        print("[INFO] Загрузка страницы oddsportal.com.")
        self.driver.get('http://www.oddsportal.com/login')
        self.driver.set_window_size(1024, 768)

    def logging_in(self, login, passw):
        '''Login in oddsportal.com'''
        try:
            print("[INFO] Вход в личный кабинет.")
            username = self.driver.find_element_by_name('login-username')
            password = self.driver.find_element_by_name('login-password')
            username.send_keys(login)
            password.send_keys(passw)
            password.send_keys('\n')
        except:
            raise Exception('You may be already login in!')

    def close_connection(self):
        self.driver.close()

def check_empty_table(tag):
    return tag.has_attr('class') and tag.has_attr('xeid') and tag.name == 'tr'

def check_tables_for_teams(tag): #Проверка на наличие таблицы с командами
    print("[INFO] Проверка на наличие таблицы с командами.")
    if tag != None:
        return True
    else:
        return False

def check_for_n_matches(tag, number_of_history_matches):
    print("[INFO] Проверка количества матчей в таблице Results.")
    if(len(tag)) < 10:
        return True

def find_matches(html, number_of_history_matches): #Поиск 10 предыдущих матчей команды
    history_matches = []
    soup = BeautifulSoup(html, 'lxml')
    table_with_matches = soup.find('table', class_='table-main')
    rows = table_with_matches.find_all(check_empty_table)
    if check_for_n_matches(rows, number_of_history_matches):
        return False
    else:
        for i in range(0, number_of_history_matches):
            match_time_td = rows[i].find('td', class_='table-time')
            match_time = match_time_td['class'][2][1:11]
            match_link = rows[i].find('td', class_='name table-participant').a.get('href')
            history_matches.append({
                'Time': match_time,
                'Link': BASE_URL + match_link
                })
    return history_matches

def find_table_of_history_matches(team_url, team_sport, team_country, team_name,
                                  number_of_history_matches):
    teams = []
    history_matches = []
    soup = BeautifulSoup(get_page(team_url), 'lxml')
    table_with_teams = soup.find('table', class_='sortable table-main')
    if check_tables_for_teams(table_with_teams):
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
                history_matches = find_matches(get_page(BASE_URL + team['Link']), number_of_history_matches)
                break
            else:
                raise Exception('No history matches for team:', team_name)
    else:
        history_matches = find_matches(get_page(team_url), number_of_history_matches)
    return history_matches

def thread_parse_history_matches(matches, phantomjs_path, login, passw):
    parsed_matches = []
    for key in matches:
        parsed_block = []
        match_node = Match(key['Link'])
        match_ratio = MatchRatio(key['Link'], phantomjs_path, login, passw)
        parsed_block.append(match_node)
        parsed_block.append(match_ratio)
        parsed_matches.append(parsed_block)
        match_node.start()
        match_ratio.start()
    return parsed_matches

def thread_matches_join(parsed_matches):
    for key in parsed_matches:
        key[0].join()
        key[1].join()
        key[0].short_show_match()
        key[0].add_ratio(key[1])
        key[0].show_match()
        key[0].show_ratio()

def print_history_matches(matches_home_team, matches_guest_team):
	#ERROR
	#Here is some error, need to correct!
    lmht = len(matches_home_team)
    lmgt = len(matches_guest_team)
    if lmht == lmgt:
        for i in range(0, lmht):
            matches_home_team[i].shortShowMatch2()
            print(' ', end = '')
            matches_guest_team[i].shortShowMatch2()
            print('\n')
    else:
        raise Exception('Something went wrong!')

def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-n", "--number", default=5)
    arg_parser.add_argument("-l", "--login", default="myparsebot")
    arg_parser.add_argument("-p", "--password", default="79213242520")
    args = vars(arg_parser.parse_args())
    number_of_history_matches = int(args["number"])
    login = str(args["login"])
    passw = str(args["password"])

    print("[INFO] Количество матчей из истории:", number_of_history_matches)
    print("[INFO] Логин:", login, "Пароль:", passw)
    start_time = time() # Настоящее время в секундах

    phantomjs_path = r"C:\Users\pingv\Documents\GitHub\oddsparser\phantomjs-2.1.1-windows\bin\phantomjs.exe"
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
         "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0"
    )
    browser = webdriver.PhantomJS(executable_path=phantomjs,
                                  desired_capabilities=dcap, service_args=["--load-images=no"])

    matches_home_team = []
    matches_guest_team = []
    match_url = input('[INFO] Введите URL матча: ')

    match_node = Match(match_url)
    match_node.start()
    match_ratio = MatchRatio(match_url, browser, login, passw)
    match_ratio.start()

    matches_home_team = find_table_of_history_matches(match_node.teamHomeURL, match_node.sport,
                                                      match_node.country, match_node.teamHome,
                                                      number_of_history_matches)
    matches_guest_team = find_table_of_history_matches(match_node.teamGuestURL, match_node.sport,
                                                       match_node.country, match_node.teamGuest,
                                                       number_of_history_matches)

    match_node.join()
    match_ratio.join()
    match_node.add_ratio(match_ratio)
    match_node.show_match()
    match_node.show_ratio()

    if (matches_home_team is not False) & (matches_guest_team is not False):
        home_m = thread_parse_history_matches(matches_home_team, browser, login, passw)
        guest_m = thread_parse_history_matches(matches_guest_team, browser, login, passw)
        thread_matches_join(home_m)
        thread_matches_join(guest_m)
    else:
        print("[ERROR] Не найдено", number_of_history_matches, "матчей в таблице Results у одной из команд.")

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
