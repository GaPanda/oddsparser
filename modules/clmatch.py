#-*- coding: utf-8 -*-

import re
from threading import Thread
from modules.clrequest import PortalRequest
from modules.clratio import MatchRatio
from time import gmtime, strftime
from bs4 import BeautifulSoup

class Match(Thread):
    def __init__(self, match_url):
        super(Match, self).__init__()
        self.started_status = False
        self.finished_status = False
        self.canceled_status = False
        self.match_url = match_url
        self.portal_request = PortalRequest(self.match_url)
        self.match_ratio = MatchRatio(self.match_url, self.portal_request)

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

    def run(self):
        soup = BeautifulSoup(self.portal_request.match_request(), 'lxml')
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
        self.team_home = match_teams[0].strip() # home team
        self.team_guest = match_teams[1].strip() # guest team
        self.team_home_url = self.create_url(self.team_home, self.sport)
        self.team_guest_url = self.create_url(self.team_guest, self.sport)
        self.match_time = gmtime(int(content.find('p')['class'][2][1:11])) # match time
        self.match_ratio.run()


    def formating_teams(self, teams):
        #ПЕРЕПИСАТЬ ИСПОЛЬЗУЯ РЕГУЛЯРКИ
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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

    def show_match(self):
        print('Sport: ', self.sport)
        print('Country: ', self.country)
        print('League: ', self.league)
        print('Teams: ', self.team_home, ' - ', self.team_guest)
        print('Time: ', strftime("%b %d %Y %H:%M:%S", self.match_time))
        try:
            print('Result:', self.temp_result)
            print('Result:', self.result)
        except:
            print('Result:', self.result)
        print('URL: ', self.match_url)
        self.match_ratio.print_ratious()

    def short_show_match(self):
        print('Teams: ', self.team_home, ' - ', self.team_guest)
        print('Time: ', strftime("%b %d %Y %H:%M:%S", self.match_time))
        try:
            print('Result:', self.temp_result)
            print('Result:', self.result)
        except:
            print('Result:', self.result)

    #def shortShowMatch2(self):
    #    print(self.match_time[2], end='')
    #    if self.result == '1':
    #        print(self.finalRatior1, end='')
    #    elif self.result == '2':
    #        print(self.finalRatior2, end='')
    #    else:
    #        print('E', end='')
