#!/usr/binenv python3

import csv, time, urllib.request
from bs4 import BeautifulSoup

BASE_URL1 = 'http://www.oddsportal.com/soccer/argentina/primera-b-nacional/'
#BASE_URL = 'http://www.oddsportal.com/soccer/belarus/vysshaya-liga/'
#BASE_URL = 'http://www.oddsportal.com/soccer/china/super-league/'
BASE_URL = 'http://www.oddsportal.com'

def get_html(url): #Получение HTML кода страницы
	
	page = urllib.request.urlopen(url)
	return page.read()

def connection(html):
	soup = BeautifulSoup(html)
	div = soup.find('div', id = 'user-header-r2')
	print(div)

def formatLeagues(leagues):
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
<<<<<<< HEAD
=======

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
				'Sport': cols[1].get_text().strip()
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

>>>>>>> testing

	soup = BeautifulSoup(html)
	table = soup.find('table', class_ = 'table-main') # Общая таблица матчей
	
<<<<<<< HEAD
	check = table.find(checkEmptyTable)

	if check != None:
		return 1
	else:
		return 0

def findResultMatchesForTeam(nodeTeam):

	def hasNoClassA(tag): #Возвращает строки не имеющие класса
		return not tag.has_attr('class') and tag.name == 'a'

	def checkEmptyTable(tag):
		return tag.has_attr('class') and tag.has_attr('xeid') and tag.name == 'tr'

	def checkTableForTeams(tag): #Проверка на наличие таблицы с командами
		if tag != None:
			return True
		else:
			return False

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
		
		for i in range(1,10):
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
				'Sport': cols[1].get_text().strip()
				})
		for team in teams:
			if team['Team'] == nodeTeam[0]['Team'] and team['Country'] == nodeTeam[0]['Country'] and team['Sport'] == nodeTeam[0]['Sport']:
				historyMatches = findMatches(get_html(BASE_URL + team['Link']))
	else:
		historyMatches = findMatches(get_html(URL))
	print('Предыдущие матчи найдены!')
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

=======

	countryAndLeague = table.find('tr', class_='dark center').find_all('a') # Нахождение тегов а с лигой и страной
	country = countryAndLeague[1].get_text().strip()
	league = countryAndLeague[2].get_text().strip() #Лига, вроде не надо

>>>>>>> testing
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

<<<<<<< HEAD
		if matchTimeFormat[7] == todayDate[7] + 1: #Не всегда будет работать, доделать!!!
=======
		if matchTimeFormat[7] == todayDate[7] + 2: #Не всегда будет работать, доделать!!!
>>>>>>> testing

			matches.append({
				'Time': matchTime,
				'Team1': teamA,
				'Team2': teamB,
				'Country': country,
				'League': league,
				'Sport' : 'Soccer',
<<<<<<< HEAD
=======
				'Status': False,
>>>>>>> testing
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
<<<<<<< HEAD
			MatchesTeam1 = []
			MatchesTeam1 = match['MatchesTeam1']
			MatchesTeam2 = []
			MatchesTeam2 = match['MatchesTeam2']
=======
			matchTeam1 = []
			matchTeam1 = match['MatchesTeam1']
			matchTeam2 = []
			matchTeam2 = match['MatchesTeam2']
>>>>>>> testing
			
			writer.writerow(
				(time.ctime(int(match['Time'])), match['Team1'], match['Team2'],\
				 match['League'], match['Country'], match['Sport'])
			)
<<<<<<< HEAD
			for key in range(0,9):	
				writer.writerow(
					(time.ctime(int(MatchesTeam1[key]['Time'])),\
					(MatchesTeam1[key]['Team1'] + ' - ' + MatchesTeam1[key]['Team2']),\
					time.ctime(int(MatchesTeam2[key]['Time'])),\
					MatchesTeam2[key]['Team1'] + ' - '+ MatchesTeam2[key]['Team2'])
				)
=======
			for i in range(0,10):	
				writer.writerow(
					(time.ctime(int(matchTeam1[i]['Time'])), matchTeam1[i]['Team1'] + ' - ' + matchTeam1[i]['Team2'],\
					 time.ctime(int(matchTeam2[i]['Time'])), matchTeam2[i]['Team1'] + ' - '+ matchTeam2[i]['Team2'])
				)
				print(i)

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

def printMatches(matches):
	i = 1
	for match in matches:
		tempMatch1 = match['MatchesTeam1']
		tempMatch2 =  match['MatchesTeam2']
		print(i,': ', match['Team1'], ' - ', match['Team2'])
		print(match['Status'])
		print(len(tempMatch1), len(tempMatch2))
		i += 1

>>>>>>> testing
			
			
def main():
	leagues = []
	matches = []
	secTime = time.time() # Настоящее время в секундах
	structTime = time.gmtime(secTime) #время в структуированном виде
<<<<<<< HEAD
	
	#Штука для тестов
	#matches.extend(parseTomorrowMatches(get_html(BASE_URL1), structTime))

	#print(matches)
	

	#Рабочая штука
	for key in leagues:
		print('Парсится лига: ', key['title'])
		if checkEmptyMatches(get_html(key['link'])) == 1:
			continue
		else:
			matches.extend(parseTomorrowMatches(get_html(key['link']),structTime))
			print('Find matches...OK')
	
	print('Всего найдено: ', len(matches))
	i = 1
=======

	leagues = parseLeagues(get_html(BASE_URL))
	leagues = formatLeagues(leagues)

	#connection(get_html(BASE_URL)) #Логин и пароль

	for key in leagues:
		print('Parsing league: ', key['title'], ' /', end = ' ')
		if checkEmptyMatches(get_html(key['link'])) == 1:
			print('Matches not found...ERROR!')
			continue
		else:
			matches.extend(parseTomorrowMatches(get_html(key['link']),structTime))
			print('Find matches...OK!')
	
	print('\nTotal matches found: ', len(matches),'\n')

	countMatches = 1
>>>>>>> testing
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
<<<<<<< HEAD
		match['MatchesTeam1'] = findResultMatchesForTeam(tempMatch1)
		match['MatchesTeam2'] = findResultMatchesForTeam(tempMatch2)
		print('Матч номер ', i, ', OK!')
		i += 1


	print('Saving...')
	save(matches, 'matches.csv')
=======
		print(match['Team1'], ' - ', match['Team2'])
		matchesHistoryTeam1 = findResultMatchesForTeam(tempMatch1)
		matchesHistoryTeam2 = findResultMatchesForTeam(tempMatch2)
		del tempMatch1, tempMatch2
		if matchesHistoryTeam1 != False and matchesHistoryTeam2 != False:
			print('Match number ', countMatches, ' is OK!')
			match['MatchesTeam1'] = matchesHistoryTeam1
			match['MatchesTeam2'] = matchesHistoryTeam2
			match['Status'] = True
			countMatches += 1
		else:
			print('Deleting match number', countMatches,'. There is no ten matches in history...')
			countMatches += 1
			continue

	matches = deleteMatches(matches)

	#print(matches)
	print('Saving...')
	
	#Переделать название сохранения!
	save(matches, 'matches.csv')

	timeEnd = time.time() - secTime

	print('The program end in: ', timeEnd/60, ' min')
>>>>>>> testing

if __name__ == '__main__':
	main()