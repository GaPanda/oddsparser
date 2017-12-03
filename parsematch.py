#-*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import time
from modules.get_html import get_page
from modules.class_match import Match
from bs4 import BeautifulSoup

BASE_URL = 'http://www.oddsportal.com'

def open_connection(driver):
    driver.get('http://www.oddsportal.com/login')
    driver.set_window_size(1024, 768)

def close_connection(driver):	
    driver.close()

def logging_in(driver):
    '''Login in oddsportal.com'''
    try:
        username = driver.find_element_by_name('login-username')
        password = driver.find_element_by_name('login-password')
        username.send_keys('myparsebot')
        password.send_keys('79213242520')
        driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div[2]/div[1]/div[2]/div/form/div[3]/button').click()
    except:
        raise Exception("Maybe you already log in.")

def checkEmptyTable(tag):
    return tag.has_attr('class') and tag.has_attr('xeid') and tag.name == 'tr'

def checkTableForTeams(tag): #Проверка на наличие таблицы с командами
    if tag != None:
        return True
    else:
        return False

def checkHistoryForTenMatches(tag):
    if(len(tag)) < 10:
        return True
	
def findMatches(html): #Поиск 10 предыдущих матчей команды	
    historyMatches = []
    soup = BeautifulSoup(html, 'lxml')
    tableWithHistoryMatches = soup.find('table', class_ = 'table-main')
    rows = tableWithHistoryMatches.find_all(checkEmptyTable)
    if checkHistoryForTenMatches(rows) == True:
        return False
    else:
        for i in range(0,5):
            matchTimeTd = rows[i].find('td', class_= 'table-time')
            matchTime = matchTimeTd['class'][2][1:11]
            matchLink = rows[i].find('td', class_= 'name table-participant').a.get('href')
            historyMatches.append({
                'Time': matchTime,
                'Link': BASE_URL + matchLink
                })
    return historyMatches

def findHistoryMatches(teamURL, teamSport, teamCountry, teamName):
    teams = []
    historyMatches = []
    soup = BeautifulSoup(get_page(teamURL), 'lxml')

    tableWithTeams = soup.find('table', class_ = 'sortable table-main')
    if checkTableForTeams(tableWithTeams) == True:
        rows = tableWithTeams.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            teams.append({
                'Team': cols[0].get_text().strip(),
                'Link': cols[0].a.get('href').strip(),
                'Country': cols[2].get_text().strip(),
                'Sport': cols[1].get_text().strip(),
                })
        for team in teams:
            if team['Team'] == teamName and team['Country'] == teamCountry and team['Sport'] == teamSport:
                historyMatches = findMatches(get_page(BASE_URL + team['Link']))
                break
            else:
                historyMatches = False
    else:
        historyMatches = findMatches(get_page(teamURL))
    return historyMatches

def parseHistoryMatches(matches, driver):
    parsed_matches = []
    count = 0
    for key in matches:
        count += 1
        print('Матч №', count ,': ')
        match_node = Match(key['Link'], driver)
        match_node.parseMatch()
        match_node.shortShowMatch()
        parsed_matches.append(match_node)
    return parsed_matches

def printHistoryMatches(matches_home_team, matches_guest_team):
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
    sec_time = time() # Настоящее время в секундах
    phantomjs_path = r"C:\Users\pingv\Documents\GitHub\oddsparser\phantomjs-2.1.1-windows\bin\phantomjs.exe"
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
        "(KHTML, like Gecko) Chrome/15.0.87"
    )
    matches_home_team = []
    matches_guest_team = []
    match_url = input('Введите URL матча: ')

    driver = webdriver.PhantomJS(executable_path=phantomjs_path, desired_capabilities=dcap)
    try:
        open_connection(driver)
        logging_in(driver)
    except Exception as err:
        print("[ERROR]", err.args[0])

    match_node = Match(match_url, driver)
    match_node.parseMatch()
    match_node.showMatch()

    matches_home_team = findHistoryMatches(match_node.teamHomeURL, match_node.sport,
                                           match_node.country, match_node.teamHome)
    matches_guest_team = findHistoryMatches(match_node.teamGuestURL, match_node.sport,
                                            match_node.country, match_node.teamGuest)
    print('\n------------------------\nМатчи домашней команды :\n------------------------')
    matches_home_team = parseHistoryMatches(matches_home_team, driver)
    print('\n------------------------\nМатчи гостевой команды :\n------------------------')
    matches_guest_team = parseHistoryMatches(matches_guest_team, driver)
    close_connection(driver)

    time_end = time() - sec_time
    print('The program end in: ', time_end/60, ' min')
    try:
        print('Finnaly:')
        printHistoryMatches(matches_home_team, matches_guest_team)
    except Exception as err:
        print('[ERROR]', err.args[0])

if __name__ == '__main__':
    main()
