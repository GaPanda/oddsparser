#-*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
from datetime import datetime
import urllib.request
from bs4 import BeautifulSoup

BASE_URL = 'http://www.oddsportal.com'

#print(datetime.datetime.fromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S')) Вывод времени нормальный

def get_html(url): #Получение HTML кода страницы
	page = urllib.request.urlopen(url)
	return page.read()

def openConnection(driver):
	driver.get('http://www.oddsportal.com/login')
	driver.set_window_size(1024, 768)

def isfloat(value):
	try:
		float(value)
		return True
	except:
		return False

def connection(driver):
    #login in oddsportal.com
    try:
        username = driver.find_element_by_name('login-username')
        password = driver.find_element_by_name('login-password')
        username.send_keys('myparsebot')
        password.send_keys('79213242520')
        driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[6]/div[1]/div/div[1]/div[2]/div[1]/div[2]/div/form/div[3]/button').click()
    except:
    	raise Exception("Maybe you already log in.")

def closeConnection(driver):	
	driver.close()

def hasNoClassA(tag): #Возвращает строки не имеющие класса
	return not tag.has_attr	('class') and tag.name == 'a'

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
	soup = BeautifulSoup(get_html(teamURL), 'lxml')

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
				historyMatches = findMatches(get_html(BASE_URL + team['Link']))
				break
			else:
				historyMatches = False
	else:
		historyMatches = findMatches(get_html(teamURL))
	return historyMatches

def parseHistoryMatches(matches, driver):
    parsedMatches = []
    count = 0
    for key in matches:
        count += 1
        print('Матч №', count ,': ')
        node = Match(key['Link'], driver)
        node.parseMatch()
        node.shortShowMatch()
        parsedMatches.append(node)
    return parsedMatches

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

class MatchRatio:
	def __init__(self, matchURL):
		self.matchURL = matchURL
		self.Bookmakers = []

	def parseRatio(self, driver): #Нахождение букмекерский контор и их коэффициентов
		driver.get(self.matchURL)
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
		
class Match:
	def __init__(self, matchURL, driver):
		self.matchURL = matchURL
		self.driver = driver
		self.ratio = MatchRatio(self.matchURL)


	def createURL(self, team_name, sport): #Создание URL ссылки из названия клуба
		URL = 'http://www.oddsportal.com/search/results/'
		TYPESPORT = '/'+ sport +'/'
		splitTeamName = team_name.split()
		urlTeamName = URL + '%20'.join(splitTeamName) + TYPESPORT.lower()
		return urlTeamName

	def formatingResults(self, result):
		if len(result) == 14:
			teamHomeScore = result[0]
			teamGuestScore = result[2]
			if teamHomeScore > teamGuestScore:
				result = '1'
			elif teamHomeScore < teamGuestScore:
				result = '2'
			elif teamHomeScore == teamGuestScore:
				result = 'X'
		else:
			result = 'Error!'
		return result

	def parseMatch(self):
		soup = BeautifulSoup(get_html(self.matchURL), 'lxml')
		content = soup.find(id = "col-content")
		divLC = soup.find(id = "breadcrumb")
		aDivLC = divLC.find_all('a')

		self.sport = aDivLC[1].get_text() # type of sport
		self.country = aDivLC[2].get_text() # match of league
		self.league = aDivLC[3].get_text() # name of league

		try:
			self.tempResult = soup.find('p', class_ = 'result').get_text()[13:]
			self.result = self.formatingResults(self.tempResult)
		except:
			self.result = 'Not started yet!'
		
		matchTeams = content.find('h1').get_text()
		matchTeams = self.formatingTeams(matchTeams)
		self.teamHome = matchTeams[0].strip() # home team
		self.teamGuest = matchTeams[1].strip() # guest team
		self.teamHomeURL = self.createURL(self.teamHome, self.sport)
		self.teamGuestURL = self.createURL(self.teamGuest, self.sport)
		self.matchTime = time.gmtime(int(content.find('p')['class'][2][1:11])) # match time

		self.ratio.parseRatio(self.driver)

		self.r1 = self.ratio.countRatio('1')
		self.finalRatior1 = self.r1[2]
		self.rX = self.ratio.countRatio('X')
		self.finalRatiorX = self.rX[2]
		self.r2 = self.ratio.countRatio('2')
		self.finalRatior2 = self.r2[2]

	def formatingTeams(self, teams):
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
		print('Country: ',self.country)
		print('League: ',self.league)
		print('Teams: ',self.teamHome,' - ',self.teamGuest)
		print('Time: ',time.strftime("%b %d %Y %H:%M:%S", self.matchTime))
		
		try:
			print('Temp Result:', self.tempResult)
			print('Result:', self.result)
		except:
			print('Result:', self.result)

		print('URL: ',self.matchURL)
		print('1: ', '[М:', self.r1[0], 'Б:', self.r1[1], '] X:', '[М:', self.rX[0], 'Б:', self.rX[1], '] 2:', '[М:', self.r2[0], 'Б:', self.r2[1], ']')
		#self.ratio.printRatious()

	def shortShowMatch(self):
		print('Teams: ',self.teamHome,' - ',self.teamGuest)
		print('Time: ',time.strftime("%b %d %Y %H:%M:%S",self.matchTime))
		try:
			print('Temp Result:', self.tempResult)
			print('Result:', self.result)
		except:
			print('Result:', self.result)
		print('URL: ',self.matchURL)
		print('1: ', '[М:', self.r1[0], 'Б:', self.r1[1], '] X:', '[М:', self.rX[0], 'Б:', self.rX[1], '] 2:', '[М:', self.r2[0], 'Б:', self.r2[1], ']')
		print('1: ', self.finalRatior1, 'X: ', self.finalRatiorX, '2: ', self.finalRatior2)
		print('------------------------')

	def shortShowMatch2(self):
		print(self.matchTime[2], end = '')
		if self.result == '1':
			print(self.finalRatior1, end = '')
		elif self.result == 'X':
			print(self.finalRatiorX,  end = '')
		elif self.result == '2':
			print(self.finalRatior2, end = '')
		else:
			print('E', end = '')

def main():
	secTime = time.time() # Настоящее время в секундах
	
	phantomjs_path = r"C:\Users\pingv\Documents\GitHub\oddsparser\phantomjs-2.1.1-windows\bin\phantomjs.exe"
	dcap = dict(DesiredCapabilities.PHANTOMJS)
	dcap["phantomjs.page.settings.userAgent"] = (
		"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
		"(KHTML, like Gecko) Chrome/15.0.87"
	)
	
	matchesHomeTeam = []
	matchesGuestTeam = []

	match_url = input('Введите URL матча: ')
	
	driver = webdriver.PhantomJS(executable_path=phantomjs_path, desired_capabilities=dcap)
	try:
		openConnection(driver)
		connection(driver)
	except Exception as err:
		print("[ERROR]", err.args[0])

	match = Match(match_url, driver)
	match.parseMatch()
	match.showMatch()

	matches_home_team = findHistoryMatches(match.teamHomeURL, match.sport, match.country, match.teamHome)
	matches_guest_team = findHistoryMatches(match.teamGuestURL, match.sport, match.country, match.teamGuest)
	print('\n------------------------\nМатчи домашней команды :\n------------------------')
	matches_home_team = parseHistoryMatches(matches_home_team, driver)
	print('\n------------------------\nМатчи гостевой команды :\n------------------------')
	matches_guest_team = parseHistoryMatches(matches_guest_team, driver)
	closeConnection(driver)

	timeEnd = time.time() - secTime

	print('The program end in: ', timeEnd/60, ' min')

	print('Finnaly:')
	try:
		printHistoryMatches(matchesHomeTeam, matchesGuestTeam)
	except Exception as err:
		print('[ERROR]', err.args[0])

if __name__ == '__main__':
	main()