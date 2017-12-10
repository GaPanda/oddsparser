#-*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import time
from modules.get_html import get_page
from modules.class_match import Match
from bs4 import BeautifulSoup
from argparse import ArgumentParser

BASE_URL = 'http://www.oddsportal.com'

def open_connection(driver):
    print("[INFO] Загрузка страницы oddsportal.com.")
    driver.get('http://www.oddsportal.com/login')
    driver.set_window_size(1024, 768)

def logging_in(driver):
    '''Login in oddsportal.com'''
    try:
        print("[INFO] Вход в личный кабинет.")
        username = driver.find_element_by_name('login-username')
        password = driver.find_element_by_name('login-password')
        username.send_keys('myparsebot')
        password.send_keys('79213242520')
        password.send_keys('\n')
    except:
        raise Exception('You may be already login in!')

def close_connection(driver):
    driver.close()

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

def parse_history_matches(matches, driver):
    parsed_matches = []
    count = 0
    for key in matches:
        count += 1
        print('Матч №', count, ': ')
        match_node = Match(key['Link'], driver)
        match_node.parseMatch()
        match_node.shortShowMatch()
        parsed_matches.append(match_node)
    return parsed_matches

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
    ap = ArgumentParser()
    ap.add_argument("-n", "--number", default=5)
    args = vars(ap.parse_args())
    number_of_history_matches = int(args["number"])
    print("[INFO] Количество матчей из истории:", number_of_history_matches)
    start_time = time() # Настоящее время в секундах
    phantomjs_path = r"C:\Users\pingv\Documents\GitHub\oddsparser\phantomjs-2.1.1-windows\bin\phantomjs.exe"
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0"
    )
    matches_home_team = []
    matches_guest_team = []
    match_url = input('[INFO] Введите URL матча: ')

    driver = webdriver.PhantomJS(executable_path=phantomjs_path,
                                 desired_capabilities=dcap, service_args=["--load-images=no"])
    try:
        open_connection(driver)
        logging_in(driver)
    except Exception as err:
        print("[WARNING]", err.args[0])

    match_node = Match(match_url, driver)
    match_node.parseMatch()
    match_node.showMatch()

    matches_home_team = find_table_of_history_matches(match_node.teamHomeURL, match_node.sport,
                                                      match_node.country, match_node.teamHome,
                                                      number_of_history_matches)
    matches_guest_team = find_table_of_history_matches(match_node.teamGuestURL, match_node.sport,
                                                       match_node.country, match_node.teamGuest,
                                                       number_of_history_matches)
    if (matches_home_team is not False) & (matches_guest_team is not False) :
        print('\n------------------------\nМатчи домашней команды :\n------------------------')
        matches_home_team = parse_history_matches(matches_home_team, driver)
        print('\n------------------------\nМатчи гостевой команды :\n------------------------')
        matches_guest_team = parse_history_matches(matches_guest_team, driver)
    else:
        print("[ERROR] Не найдено", number_of_history_matches, "матчей в таблице Results у одной из команд.")
    close_connection(driver)

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
