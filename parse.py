#!/usr/binenv python3

import csv, time, urllib.request, sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

BASE_URL = 'http://www.oddsportal.com'

def get_html(url): #Получение HTML кода страницы
	page = urllib.request.urlopen(url)
	return page.read()

def formatLeagues(leagues): #Переделать
	leagues.pop(0)
	leagues.pop(0)
	leagues.pop(0)
	leagues.pop(0)
	leagues.pop(0)
	leagues.pop(0)
	leagues.pop(0)
	leagues.pop(0)
	return leagues

def parseLeagues(html): #Парсинг ссылок для лиг
	leagues = []

	soup = BeautifulSoup(html)
	table = soup.find('div', id = 's_1')
	li = table.find_all('li', class_ = 'tournament') #Убрать Popular из списка!!!

	for key in li:
		league = key.find('a').get_text()
		leagueLink = key.find('a').get('href')
		fullLeagueLink = BASE_URL + leagueLink
		leagues.append({
			'title': league,
			'link': fullLeagueLink
			})

	return leagues

def checkEmptyMatches(html):
	def checkEmptyTable(tag):
		return not tag.has_attr('class') and not tag.has_attr('xeid') and tag.name == 'tr'

	soup = BeautifulSoup(html)
	table = soup.find('table', class_ = 'table-main') # Общая таблица матчей
	
	check = table.find(checkEmptyTable)

	if check != None:
		return 1
	else:
		return 0

def findResultMatchesForTeam(nodeTeam):

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

	def createURL(teamName): #Создание URL ссылки из названия клуба
		URL = 'http://www.oddsportal.com/search/results/'
		TYPESPORT = '/soccer/'
		splitTeamName = teamName.split()
		urlTeamName = URL + '%20'.join(splitTeamName) + TYPESPORT
		return urlTeamName

	def findMatches(html): #Поиск 10 предыдущих матчей команды
		
		historyMatches = []

		soup = BeautifulSoup(html)
		tableWithHistoryMatches = soup.find('table', class_ = 'table-main')
		rows = tableWithHistoryMatches.find_all(checkEmptyTable)
		
		if checkHistoryForTenMatches(rows) == True:
			return False
		else:
			for i in range(0,10):
				matchTimeTd = rows[i].find('td', class_= 'table-time')
				matchTime = matchTimeTd['class'][2][1:11]
				matchLink = rows[i].find('td', class_= 'name table-participant').a.get('href')
				teams = rows[i].find('td', class_= 'name table-participant').find(hasNoClassA).get_text().split()
				A = []
				B = []
				i = 0
				position = 0 #Индекс тире в строке		
				for key in teams:
					if position == 0 and teams[i] != '-':
						A.append(teams[i])
					elif teams[i] == '-':
						position = i
					elif position != 0:
						B.append(teams[i])
					i += 1	

				teamA = ' '.join(A)
				teamB = ' '.join(B)

				historyMatches.append({
					'Time': matchTime,
					'Link': BASE_URL + matchLink,
					'Team1': teamA,
					'Team2': teamB,
					'Ratios': [],
					'Ratio': ''
					})

			return historyMatches

	teams = []
	historyMatches = []

	URL = createURL(nodeTeam[0]['Team'])
	soup = BeautifulSoup(get_html(URL))

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
				'Coefficient': []
				})
		for team in teams:
			if team['Team'] == nodeTeam[0]['Team'] and team['Country'] == nodeTeam[0]['Country'] and team['Sport'] == nodeTeam[0]['Sport']:
				historyMatches = findMatches(get_html(BASE_URL + team['Link']))
				break
			else:
				historyMatches = False
	else:
		historyMatches = findMatches(get_html(URL))

	return historyMatches

def parseTomorrowMatches(html, todayDate): #Парсинг конкретной лиги
	
	matches = []

	def hasNoClassTr(tag): #Возвращает строки не имеющие класса
		return not tag.has_attr('class') and tag.name == 'tr'

	def hasNoClassA(tag): #Возвращает строки не имеющие класса
		return not tag.has_attr('class') and tag.name == 'a'

	soup = BeautifulSoup(html)
	table = soup.find('table', class_ = 'table-main') # Общая таблица матчей
	
	countryAndLeague = table.find('tr', class_='dark center').find_all('a') # Нахождение тегов а с лигой и страной
	country = countryAndLeague[1].get_text().strip()
	league = countryAndLeague[2].get_text().strip() #Лига, вроде не надо

	rows1 = table.find_all(hasNoClassTr)
	rows2 = table.find_all('tr', class_ = 'odd') # поиск матчей
	rows = rows1 + rows2

	for row in rows:
		matchTimeTd = row.find('td', class_= 'table-time')
		matchTime = matchTimeTd['class'][2][1:11]
		teams = row.find('td', class_= 'name table-participant').find(hasNoClassA).get_text().split()
		A = []
		B = []
		i = 0

		position = 0 #Индекс тире в строке		
		for key in teams:
			if position == 0 and teams[i] != '-':
				A.append(teams[i])
			elif teams[i] == '-':
				position = i
			elif position != 0:
				B.append(teams[i])
			i += 1	

		teamA = ' '.join(A)
		teamB = ' '.join(B)
			
		matchTimeFormat = time.gmtime(int(matchTime)) # Преобразование времени в вид кортежа

		if matchTimeFormat[7] == todayDate[7] + 2: #Не всегда будет работать, доделать!!!

			matches.append({
				'Time': matchTime,
				'Team1': teamA,
				'Team2': teamB,
				'Country': country,
				'League': league,
				'Sport' : 'Soccer',
				'Status': False,
				'MatchesTeam1': [],
				'MatchesTeam2': []
				})
		else:
			continue
	return matches

def save(matches, path):
	with open(path, 'w') as cvsfile:
		writer = csv.writer(cvsfile)

		writer.writerow(('Дата', 'Команда1', 'Команда2', 'Лига', 'Страна', 'Спорт'))
		
		for match in matches:
			matchTeam1 = []
			matchTeam1 = match['MatchesTeam1']
			matchTeam2 = []
			matchTeam2 = match['MatchesTeam2']
			
			writer.writerow(
				(time.ctime(int(match['Time'])), match['Team1'], match['Team2'],\
				 match['League'], match['Country'], match['Sport'])
			)
			for i in range(0,10):	
				writer.writerow(
					(time.ctime(int(matchTeam1[i]['Time'])), matchTeam1[i]['Team1'] + ' - ' + matchTeam1[i]['Team2'],\
					matchTeam1[i]['Ratio'],\
					time.ctime(int(matchTeam2[i]['Time'])), matchTeam2[i]['Team1'] + ' - '+ matchTeam2[i]['Team2'],\
					matchTeam2[i]['Ratio'])
				)

def deleteMatches(matches):
	totalMatches = len(matches)
	cur = 0
	for key in range(0, totalMatches):
		if matches[cur]['Status'] == False:
			matches.pop(cur)
			totalMatches -= 1
		else:
			cur += 1
			continue
	return matches

def openConnection(driver):
	driver.set_window_size(1024, 768) # optional
	driver.get('http://www.oddsportal.com')
	connectionError = ''
	try:
		username = driver.find_element_by_name('login-username')
		password = driver.find_element_by_name('login-password')
		username.send_keys('myparsebot')
		password.send_keys('79213242520')
		driver.find_element_by_name('login-submit').click()
	except connectionError:
		print('Connection error')

def closeConnection(driver):
	driver.close()

def parsePage(driver, page):

	ratious = []
	
	def teamResult(str):
		if len(str) == 14:
			team1 = str[0]
			team2 = str[2]
			if team1 > team2:
				result = 2
			elif team1 < team2:
				result = 4
			elif team1 == team2:
				result = 3
		else:
			result = 3
		return result

	driver.get(page)
	result = driver.find_element_by_css_selector('p.result').text[13:]
	teamResult = teamResult(result)
	rows = driver.find_elements_by_xpath(('//*[@id="odds-data-table"]/div[1]/table/tbody/tr/td[' + str(teamResult) + ']'))
	count = 0
	for row in rows:
		hov = ActionChains(driver).move_to_element(row)
		hov.perform()
		data_in_the_bubble = driver.find_element_by_xpath("//*[@id='tooltiptext']")
		hover_data = BeautifulSoup(data_in_the_bubble.get_attribute("innerHTML"))
		data = hover_data.find_all('strong')
		if len(data) > 1:
			lastRatio = data[0].get_text()
			firstRatio = data[len(data)-1].get_text()
			if lastRatio < firstRatio:
				ratious.append('М')
			elif lastRatio > firstRatio:
				ratious.append('Б')
			else:
				continue
		else:
			continue
	return ratious

def printMatches(matches):
	i = 1
	for match in matches:
		tempMatch1 = match['MatchesTeam1']
		tempMatch2 =  match['MatchesTeam2']
		print(i,': ', match['Team1'], ' - ', match['Team2'])
		print(match['Status'])
		print(len(tempMatch1), len(tempMatch2))
		i += 1

def ratiousSum(ratious):
	countM = 0
	countB = 0
	finalResult = ''
	for ratio in ratious:
		if ratio == 'М':
			countM += 1
		if ratio == 'Б':
			countB += 1
	if countM < countB:
		finalResult = 'Б'
	elif countM > countB:
		finalResult = 'М'
	else:
		finalResult = 'Б/М'
	return finalResult
			
			
def main():
	leagues = []
	matches = []
	secTime = time.time() # Настоящее время в секундах
	structTime = time.gmtime(secTime) #время в структуированном виде

	leagues = parseLeagues(get_html(BASE_URL))
	leagues = formatLeagues(leagues)

	for key in leagues:
		print('Parsing league: ', key['title'], end = ' / ')
		if checkEmptyMatches(get_html(key['link'])) == 1:
			print('Matches not found...ERROR!')
			continue
		else:
			matches.extend(parseTomorrowMatches(get_html(key['link']),structTime))
			print('Find matches...OK!')
	
	print('\nTotal matches found: ', len(matches),'\n')

	countMatches = 1

	for match in matches:
		tempMatch1 = [{
		'Team': match['Team1'],
		'Sport': match['Sport'],
		'Country': match['Country']
		}]
		tempMatch2 = [{
		'Team': match['Team2'],
		'Sport': match['Sport'],
		'Country': match['Country']
		}]
		print(countMatches,': ', match['Team1'], ' - ', match['Team2'], end = " / ")
		matchesHistoryTeam1 = findResultMatchesForTeam(tempMatch1)
		matchesHistoryTeam2 = findResultMatchesForTeam(tempMatch2)
		del tempMatch1, tempMatch2
		if matchesHistoryTeam1 != False and matchesHistoryTeam2 != False:
			print('Match is OK!')
			match['MatchesTeam1'] = matchesHistoryTeam1
			match['MatchesTeam2'] = matchesHistoryTeam2
			match['Status'] = True
			countMatches += 1
		else:
			print('Deleting match. There is no ten matches in history...')
			countMatches += 1
			continue

	matches = deleteMatches(matches)

	print('Matches after deleting: ', len(matches))
	print('Starting checking coefficient...')

	driver = webdriver.PhantomJS() # or add to your PATH
	openConnection(driver)

	count = 0
	for match in matches:
		for i in range(0,10):
			try:
				#Матчи команды А
				ratioTeamA = parsePage(driver, match['MatchesTeam1'][i]['Link'])
				match['MatchesTeam1'][i]['Ratious'] = ratioTeamA
				#Матчи команды B
				ratioTeamB = parsePage(driver, match['MatchesTeam2'][i]['Link'])
				match['MatchesTeam2'][i]['Ratious'] = ratioTeamB
				if len(match['MatchesTeam1'][i]['Ratious']) < 10 or len(match['MatchesTeam2'][i]['Ratious']) < 10:
					match['Status'] = False
					break
				else:
					match['MatchesTeam1'][i]['Ratio'] = ratiousSum(ratioTeamA)
					match['MatchesTeam2'][i]['Ratio'] = ratiousSum(ratioTeamB)
			except:
				match['Status'] = False
				break
			else:
				print('Parsing ratious %d%%' % (count / len(matches) * 100))
		count += 1
	closeConnection(driver)
	
	matches = deleteMatches(matches)
	
	print('\nSaving...')
	
	save(matches, 'matches.csv')

	timeEnd = time.time() - secTime

	print('The program end in: ', timeEnd/60, ' min')

if __name__ == '__main__':
	main()