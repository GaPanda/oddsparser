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
        #Rewrite!!!! errors!!!!
        if len(result) == 14:
            team_home_score = result[0]
            team_guest_score = result[2]
            if team_home_score > team_guest_score:
                result = '1'
            elif team_home_score < team_guest_score:
                result = '2'
            elif team_home_score == team_guest_score:
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
            self.result = 'Not started yet!'

        matchTeams = content.find('h1').get_text()
        matchTeams = self.formating_teams(matchTeams)
        self.teamHome = matchTeams[0].strip() # home team
        self.teamGuest = matchTeams[1].strip() # guest team
        self.teamHomeURL = self.create_url(self.teamHome, self.sport)
        self.teamGuestURL = self.create_url(self.teamGuest, self.sport)
        self.matchTime = gmtime(int(content.find('p')['class'][2][1:11])) # match time

        self.ratio.parseRatio(self.driver)

        self.r1 = self.ratio.countRatio('1')
        self.finalRatior1 = self.r1[2]
        self.rX = self.ratio.countRatio('X')
        self.finalRatiorX = self.rX[2]
        self.r2 = self.ratio.countRatio('2')
        self.finalRatior2 = self.r2[2]

    def formating_teams(self, teams):
        matchTeams = []
        _teamA = []
        _teamB = []
        i = 0
        position = 0 #Индекс тире в строке		
        for key in teams:
            if position == 0 and teams[i] != '-':
                _teamA.append(teams[i])
            elif teams[i] == '-':
                position = i
            elif position != 0:
                _teamB.append(teams[i])
            i += 1
        teamA = ''.join(_teamA)
        teamB = ''.join(_teamB)
        matchTeams.append(teamA)
        matchTeams.append(teamB)
        return matchTeams

    def showMatch(self):
        print('Sport: ', self.sport)
        print('Country: ', self.country)
        print('League: ', self.league)
        print('Teams: ', self.teamHome, ' - ', self.teamGuest)
        print('Time: ', strftime("%b %d %Y %H:%M:%S", self.matchTime))	
        try:
            print('Temp Result:', self.temp_result)
            print('Result:', self.result)
        except:
            print('Result:', self.result)

        print('URL: ', self.match_url)
        print('1: ', '[М:', self.r1[0], 'Б:', self.r1[1], '] X:', '[М:', self.rX[0], \
                'Б:', self.rX[1], '] 2:', '[М:', self.r2[0], 'Б:', self.r2[1], ']')
        #self.ratio.printRatious()

    def shortShowMatch(self):
        print('Teams: ', self.teamHome, ' - ', self.teamGuest)
        print('Time: ', strftime("%b %d %Y %H:%M:%S", self.matchTime))
        try:
            print('Temp Result:', self.temp_result)
            print('Result:', self.result)
        except:
            print('Result:', self.result)
        print('URL: ', self.match_url)
        print('1: ', '[М:', self.r1[0], 'Б:', self.r1[1], '] X:', '[М:', self.rX[0], \
                'Б:', self.rX[1], '] 2:', '[М:', self.r2[0], 'Б:', self.r2[1], ']')
        print('1: ', self.finalRatior1, 'X: ', self.finalRatiorX, '2: ', self.finalRatior2)
        print('------------------------')

    def shortShowMatch2(self):
        print(self.matchTime[2], end = '')
        if self.result == '1':
            print(self.finalRatior1, end = '')
        elif self.result == 'X':
            print(self.finalRatiorX, end = '')
        elif self.result == '2':
            print(self.finalRatior2, end = '')
        else:
            print('E', end = '')

class MatchRatio:
    def __init__(self, match_url):
        self.match_url = match_url
        self.Bookmakers = []

    def parseRatio(self, driver): #Нахождение букмекерский контор и их коэффициентов
        driver.get(self.match_url)
        rows = driver.find_elements_by_class_name('lo')
        for row in rows:
            elements = row.find_elements_by_tag_name('td')
            div = elements[0].find_element_by_class_name('l')
            tag_a = div.find_elements_by_tag_name('a')
            nameBookmaker = tag_a[1].text
            ratio_1 = self.ratious(driver, elements[1])
            ratio_X = self.ratious(driver, elements[2])
            ratio_2 = self.ratious(driver, elements[3])
            self.Bookmakers.append(Bookmaker(nameBookmaker, ratio_1, ratio_X, ratio_2))

    def ratious(self, driver, element): #Обработка разницы начального и конечного коэффициента
        ratio = ''
        hov = ActionChains(driver).move_to_element(element)
        hov.perform()
        data_in_the_bubble = driver.find_element_by_xpath("//*[@id='tooltiptext']")
        hover_data = BeautifulSoup(data_in_the_bubble.get_attribute("innerHTML"), "lxml")
        temp_data = hover_data.find_all('strong')
        data = self.correctRatio(temp_data)
        if len(data) > 1:
            lastRatio = data[0].get_text().strip()
            firstRatio = data[len(data)-1].get_text().strip()
            if isfloat(lastRatio) & isfloat(firstRatio): #Не обязательное условие
                if (bool(lastRatio) != False) & (bool(firstRatio) != False) & (lastRatio < firstRatio):
                    ratio = 'Lower'
                elif (bool(lastRatio) != False) & (bool(firstRatio) != False) & (lastRatio > firstRatio):
                    ratio = 'Higher'
                else:
                    ratio = 'Equal'
        else:
            ratio = 'Error'
        return ratio

    def countRatio(self, result):
        Lower = []
        Higher = []
        for Bookmaker in self.Bookmakers:
            ratio = Bookmaker.returnRatio(result)
            if ratio == 'Higher':
                Higher.append(ratio)
            elif ratio == 'Lower':
                Lower.append(ratio)
            else:
                continue
        lenLower = len(Lower)
        lenHigher = len(Higher)
        if lenLower < lenHigher:
            finalRatio = 'Higher'
        elif lenLower > lenHigher:
            finalRatio = 'Lower'
        else:
            finalRatio = 'Equal'
        counts = [len(Lower), len(Higher), finalRatio]
        return counts

    def correctRatio(self, value): #Удаление ненужной строки из коэффициентов
        length = len(value)
        if isfloat(value[length-1].get_text()):
            return value
        else:
            value.pop(length-1)
            return value

    def printRatious(self):
        for Bookmaker in self.Bookmakers:
            Bookmaker.printBookmaker()

class Bookmaker:
    def __init__(self, nameBookmaker, ratio_1, ratio_X, ratio_2):
        self.nameBookmaker = nameBookmaker
        self.ratio_1 = ratio_1
        self.ratio_X = ratio_X
        self.ratio_2 = ratio_2

    def printBookmaker(self):
        print('Bookmaker: ', self.nameBookmaker)
        print('1: ', self.ratio_1)
        print('X: ', self.ratio_X)
        print('2: ', self.ratio_2)

    def checkRatioErrors(self):
        if self.ratio_1 == 'Higher' and self.ratio_2 == 'Higher' and self.ratio_X == 'Higher':
            return False
        else:
            return True

    def returnRatio(self, result):
        if result == '1':
            if self.checkRatioErrors() and (self.ratio_1 == 'Higher' or self.ratio_1 == 'Lower'):
                return self.ratio_1
            else:
                return
        elif result == 'X':
            if self.checkRatioErrors() and (self.ratio_X == 'Higher' or self.ratio_X == 'Lower'):
                return self.ratio_X
            else:
                return
        elif result == '2':
            if self.checkRatioErrors() and (self.ratio_2 == 'Higher' or self.ratio_2 == 'Lower'):
                return self.ratio_2
            else:
                return
        else:
            print('Error with result!')
            