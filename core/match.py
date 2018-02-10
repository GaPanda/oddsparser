#-*- coding: utf-8 -*-

import re
from urllib.request import urlopen, unquote, Request
from threading import Thread
from time import gmtime, strftime
from bs4 import BeautifulSoup

feed_url = 'http://fb.oddsportal.com/feed/'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 YaBrowser/17.11.1.990 Yowser/2.5 Safari/537.36'

class Match(Thread):
    def __init__(self, match_url):
        super(Match, self).__init__()
        self.match_url = match_url
        self.match_ratio = None
        self.match_result = None

    def add_data(self, ratio, result):
        self.match_ratio = ratio
        self.match_result = result

    def return_keys(self):
        return self.xhash, self.id_sport, self.id_match, self.id_version

    def match_request(self):
        request = Request(self.match_url)
        request.add_header('referer', self.match_url)
        request.add_header('user-agent', user_agent)
        html = urlopen(request).read().decode('utf-8')
        self.xhash = unquote(re.search('"xhash":"(.+?)"', html).group(1))
        self.id_match = re.search('"id":"(.+?)"', html).group(1)
        self.id_sport = re.search('"sportId":(.+?)', html).group(1)
        self.id_version = re.search('"versionId":(.+?)', html).group(1)
        return html

    def run(self):
        html = self.match_request()
        soup = BeautifulSoup(html, 'lxml')
        content = soup.find(id="col-content")
        div_lc = soup.find(id="breadcrumb")
        a_div_lc = div_lc.find_all('a')
        self.sport = a_div_lc[1].get_text() # type of sport
        self.country = a_div_lc[2].get_text() # match of league
        self.league = a_div_lc[3].get_text() # name of league
        match_teams = self.formating_teams(content.find('h1').get_text())
        self.team_home = match_teams[0].strip() # home team
        self.team_guest = match_teams[1].strip() # guest team
        self.match_time = int(content.find('p')['class'][2][1:11]) # match time

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
        print('Sport:', self.sport)
        print('Country:', self.country)
        print('League:', self.league)
        print('Teams:', self.team_home, ' - ', self.team_guest)
        print('Time:', strftime("%b %d %Y %H:%M:%S", gmtime(self.match_time)))
        print('URL: ', self.match_url)
        self.match_result.print_result()
        self.match_ratio.print_ratious()

    def short_show_match(self):
        print('Teams: ', self.team_home, ' - ', self.team_guest)
        print('Time: ', strftime("%b %d %Y %H:%M:%S", gmtime(self.match_time)))
        print('Result:', result.value)
        match_ratio.print_ratious()
