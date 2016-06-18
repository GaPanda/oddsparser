#!/usr/binenv python3

import csv
import time
from datetime import datetime
import urllib.request
from bs4 import BeautifulSoup

BASE_URL1 = 'http://www.oddsportal.com/soccer/argentina/primera-b-nacional/'
#BASE_URL = 'http://www.oddsportal.com/soccer/belarus/vysshaya-liga/'
#BASE_URL = 'http://www.oddsportal.com/soccer/china/super-league/'
BASE_URL = 'http://www.oddsportal.com'

#print(datetime.datetime.fromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S')) Вывод времени нормальный

def get_html(url): #Получение HTML кода страницы
	
	page = urllib.request.urlopen(url)
	return page.read()

def parseLeagues(html): #Парсинг ссылок для лиг
	
	leagues = []

	soup = BeautifulSoup(html)
	table = soup.find('div', id = 's_1')
	li = table.find_all('li', class_ = 'tournament')

	for key in li:
		league = key.find('a').get_text()
		leagueLink = key.find('a').get('href')
		fullLeagueLink = BASE_URL + leagueLink
		leagues.append({
			'title': league,
			'link': fullLeagueLink
			})

	return leagues


def parseTomorrowMatches(html, todayDate): #Парсинг конкретной лиги
	
	matches = []

	def hasNoClassTr(tag): #Возвращает строки не имеющие класса
		return not tag.has_attr('class') and tag.name == 'tr'

	def hasNoClassA(tag): #Возвращает строки не имеющие класса
		return not tag.has_attr('class') and tag.name == 'a'

	def checkEmpty(tag):
		return not tag.has_attr('class') and not tag.has_attr('xeid') and tag.name == 'tr'

	soup = BeautifulSoup(html)
	table = soup.find('table', class_ = 'table-main') # Общая таблица матчей
	
	check = table.find(checkEmpty)
	
	if check != None:
		return 1
	else:
		countryAndLeague = table.find('tr', class_='dark center').find_all('a') # Нахождение тегов а с лигой и страной
		country = countryAndLeague[1].get_text().strip()
		league = countryAndLeague[2].get_text().strip() #Лига, вроде не надо

		rows1 = table.find_all(hasNoClassTr)
		rows2 = table.find_all('tr', class_ = 'odd') # поиск матчей
		rows = rows1 + rows2

		for row in rows:
			matchTimeTd = row.find('td', class_= 'table-time')
			matchTime = matchTimeTd['class'][2][1:11]
			#print(time.gmtime(int(matchTime)))
			#teams = row.find('td', class_= 'name table-participant').get_text().split()
			teams = row.find('td', class_= 'name table-participant').find(hasNoClassA).get_text().split()
			A = []
			B = []
			i = 0
			position = 0
			
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

			if matchTimeFormat[7] == todayDate[7] + 1: #Костыль
				matches.append({
					'Time': matchTime,
					'Team1': teamA,
					'Team2': teamB,
					'Country': country,
					'League': league,
					'Sport' : 'Soccer'
					})
			else:
				continue

		return matches

def save(matches, path):
	with open(path, 'w') as cvsfile:
		writer = csv.writer(cvsfile)

		writer.writerow(('Дата', 'Команда1', 'Команда2', 'Лига', 'Страна', 'Спорт'))

		writer.writerows(
				(match['Time'], match['Team1'], match['Team2'], match['League'], match['Country'], match['Sport']) for match in matches
			)	

def main():
	leagues = []
	matches = []
	leagues = parseLeagues(get_html(BASE_URL))
	
	secTime = time.time() # Настоящее время в секундах
	structTime = time.gmtime(secTime) #время в структуированном виде
	
	#Штука для тестов
	#matches.extend(parseTomorrowMatches(get_html(BASE_URL1), structTime))
	#print(matches)
	
	#Рабочая штука
	for key in leagues:
		print(key['link'])
		if parseTomorrowMatches(get_html(key['link']),structTime) == 1: # вот тут надо изменить!!!!!!
			continue
		else:
			matches.extend(parseTomorrowMatches(get_html(key['link']),structTime))

	print(matches)
	#print('Saving...')
	#save(matches, 'matches.csv')

if __name__ == '__main__':
	main()