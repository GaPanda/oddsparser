import re
from time import gmtime, strftime
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from modules.get_html import get_page

def isfloat(value):
    try:
        float(value)
        return True
    except:
        return False

class Match:
    def __init__(self, match_url, driver):
        self.match_url = match_url
        self.driver = driver
        self.ratio = MatchRatio(self.match_url)

    def create_url(self, team_name, sport): #Создание URL ссылки из названия клуба
        url = 'http://www.oddsportal.com/search/results/'
        typesport = '/'+ sport +'/'
        split_team_name = team_name.split()
        url_team_name = url + '%20'.join(split_team_name) + typesport.lower()
        return url_team_name

    def formating_results(self, result):
        regex = r"((\d*)[\:](\d*))"
        re_result = re.search(regex, result)
        team_home_score = re_result[2]
        team_guest_score = re_result[3]
        if int(team_home_score) > int(team_guest_score):
            result = '1'
        elif int(team_home_score) < int(team_guest_score):
            result = '2'
        elif int(team_home_score) == int(team_guest_score):
            result = 'X'
        else:
            result = 'Error!'
        return result

    def parseMatch(self):
        soup = BeautifulSoup(get_page(self.match_url), 'lxml')
        content = soup.find(id="col-content")
        div_lc = soup.find(id="breadcrumb")
        a_div_lc = div_lc.find_all('a')

        self.sport = a_div_lc[1].get_text() # type of sport
        self.country = a_div_lc[2].get_text() # match of league
        self.league = a_div_lc[3].get_text() # name of league
        try:
            self.temp_result = soup.find('p', class_='result').get_text()[13:]
            self.result = self.formating_results(self.temp_result)
        except:
            self.result = 'Error or not started yet!'

        match_teams = content.find('h1').get_text()
        match_teams = self.formating_teams(match_teams)
        self.teamHome = match_teams[0].strip() # home team
        self.teamGuest = match_teams[1].strip() # guest team
        self.teamHomeURL = self.create_url(self.teamHome, self.sport)
        self.teamGuestURL = self.create_url(self.teamGuest, self.sport)
        self.match_time = gmtime(int(content.find('p')['class'][2][1:11])) # match time

        self.ratio.parseRatio(self.driver)

        self.r1 = self.ratio.countRatio('1')
        self.finalRatior1 = self.r1[4]
        self.r2 = self.ratio.countRatio('2')
        self.finalRatior2 = self.r2[4]

    def formating_teams(self, teams):
        match_teams = []
        team_a = []
        team_b = []
        i = 0
        position = 0 #Индекс тире в строке		
        for key in teams:
            if position == 0 and teams[i] != '-':
                team_a.append(teams[i])
            elif teams[i] == '-':
                position = i
            elif position != 0:
                team_b.append(teams[i])
            i += 1
        teamA = ''.join(team_a)
        teamB = ''.join(team_b)
        match_teams.append(teamA)
        match_teams.append(teamB)
        return match_teams

    def showMatch(self):
        print('Sport: ', self.sport)
        print('Country: ', self.country)
        print('League: ', self.league)
        print('Teams: ', self.teamHome, ' - ', self.teamGuest)
        print('Time: ', strftime("%b %d %Y %H:%M:%S", self.match_time))	
        try:
            print('Temp Result:', self.temp_result)
            print('Result:', self.result)
        except:
            print('Result:', self.result)

        print('URL: ', self.match_url)
        print('1:', '[М:', self.r1[0], 'Б:', self.r1[1], 'E:', self.r1[2], 'SUM:', self.r1[3], ']', \
              '2:', '[М:', self.r2[0], 'Б:', self.r2[1], 'E:', self.r2[2], 'SUM:', self.r2[3], ']')
        #self.ratio.print_ratious()

    def shortShowMatch(self):
        print('Teams: ', self.teamHome, ' - ', self.teamGuest)
        print('Time: ', strftime("%b %d %Y %H:%M:%S", self.match_time))
        try:
            print('Temp Result:', self.temp_result)
            print('Result:', self.result)
        except:
            print('Result:', self.result)
        print('1:', '[М:', self.r1[0], 'Б:', self.r1[1], 'E:', self.r1[2], 'SUM:', self.r1[3], ']', \
              '2:', '[М:', self.r2[0], 'Б:', self.r2[1], 'E:', self.r2[2], 'SUM:', self.r2[3], ']')
        print('1: [' + self.finalRatior1 + '] 2: [' + self.finalRatior2 + ']')
        print('------------------------')

    def shortShowMatch2(self):
        print(self.match_time[2], end='')
        if self.result == '1':
            print(self.finalRatior1, end='')
        elif self.result == '2':
            print(self.finalRatior2, end='')
        else:
            print('E', end='')

class MatchRatio:
    def __init__(self, match_url):
        self.match_url = match_url
        self.Bookmakers = []

    def parseRatio(self, driver): #Нахождение букмекерский контор и их коэффициентов
        driver.get(self.match_url)
        rows = driver.find_elements_by_class_name('lo')
        self.len_rows = len(rows)
        for row in rows:
            elements = row.find_elements_by_tag_name('td')
            div = elements[0].find_element_by_class_name('l')
            tag_a = div.find_elements_by_tag_name('a')
            name_bookmaker = tag_a[1].text
            ratio_1 = self.ratious(driver, elements[1])               
            ratio_2 = self.ratious(driver, elements[2])
            self.Bookmakers.append(Bookmaker(name_bookmaker, ratio_1, ratio_2))

    def ratious(self, driver, element): #Обработка разницы начального и конечного коэффициента
        ratio = ''
        hov = ActionChains(driver).move_to_element(element)
        hov.perform()
        try:
            data_in_the_bubble = driver.find_element_by_xpath("//*[@id='tooltiptext']")
        except:
            ratio = 'Error'
            return ratio
        hover_data = BeautifulSoup(data_in_the_bubble.get_attribute("innerHTML"), "lxml")
        temp_data = hover_data.find_all('strong')
        data = self.correct_ratio(temp_data)
        if len(data) > 1:
            last_ratio = data[0].get_text().strip()
            first_ratio = data[len(data)-1].get_text().strip()
            if isfloat(last_ratio) & isfloat(first_ratio): #Не обязательное условие
                if (bool(last_ratio) != False) & (bool(first_ratio) != False) & (last_ratio < first_ratio):
                    ratio = 'Lower'
                elif (bool(last_ratio) != False) & (bool(first_ratio) != False) & (last_ratio > first_ratio):
                    ratio = 'Higher'
                else:
                    ratio = 'Equal'
        else:
            ratio = 'Error'
        return ratio

    def countRatio(self, result):
        procents = 85
        lower = []
        higher = []
        error = []
        for key in self.Bookmakers:
            ratio = key.returnRatio(result)
            if ratio == 'Higher':
                higher.append(ratio)
            elif ratio == 'Lower':
                lower.append(ratio)
            elif ratio == 'Error':
                error.append(ratio)
            else:
                continue
        len_lower = len(lower)
        len_higher = len(higher)
        if (len_lower / self.len_rows * 100) > procents:
            final_ratio = 'Higher'
        elif (len_higher / self.len_rows * 100) > procents:
            final_ratio = 'Lower'
        else:
            final_ratio = 'Error'
        counts = [len(lower), len(higher), len(error), self.len_rows, final_ratio]
        return counts

    def correct_ratio(self, value): #Удаление ненужной строки из коэффициентов
        length = len(value)
        if isfloat(value[length-1].get_text()):
            return value
        else:
            value.pop(length-1)
            return value

    def print_ratious(self):
        for Bookmaker in self.Bookmakers:
            Bookmaker.printBookmaker()

class Bookmaker:
    def __init__(self, name_bookmaker, ratio_1, ratio_2):
        self.name_bookmaker = name_bookmaker
        self.ratio_1 = ratio_1
        self.ratio_2 = ratio_2

    def printBookmaker(self):
        print('Bookmaker: ', self.name_bookmaker)
        print('1: ', self.ratio_1)
        print('2: ', self.ratio_2)

    def checkRatioErrors(self):
        if self.ratio_1 == 'Higher' and self.ratio_2 == 'Higher':
            return False
        else:
            return True

    def returnRatio(self, result):
        if result == '1':
            if self.checkRatioErrors() and (self.ratio_1 == 'Higher' or self.ratio_1 == 'Lower'):
                return self.ratio_1
            else:
                return
        elif result == '2':
            if self.checkRatioErrors() and (self.ratio_2 == 'Higher' or self.ratio_2 == 'Lower'):
                return self.ratio_2
            else:
                return
        else:
            print('Error with result!')
            