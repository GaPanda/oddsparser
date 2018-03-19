# -*- coding: utf-8 -*-

import re
import core.request
from urllib.request import unquote
from threading import Thread
from time import gmtime, strftime
from bs4 import BeautifulSoup


class Match(Thread):
    def __init__(self, match_url):
        super(Match, self).__init__()
        self.match_url = match_url
        self.match_ratio = None
        self.match_result = None
        self.xhash = None
        self.id_sport = None
        self.id_match = None
        self.id_version = None

    def add_data(self, ratio, result):
        self.match_ratio = ratio
        self.match_result = result

    def return_keys(self):
        return self.xhash, self.id_sport, self.id_match, self.id_version

    def run(self):
        html = core.request.page_request(self.match_url)

        self.xhash = unquote(re.search('"xhash":"(.+?)"', html).group(1))
        self.id_match = re.search('"id":"(.+?)"', html).group(1)
        self.id_sport = re.search('"sportId":(.+?)', html).group(1)
        self.id_version = re.search('"versionId":(.+?)', html).group(1)

        soup = BeautifulSoup(html, 'lxml')
        content = soup.find(id="col-content")
        div_lc = soup.find(id="breadcrumb")
        a_div_lc = div_lc.find_all('a')

        self.sport = a_div_lc[1].get_text()
        self.country = a_div_lc[2].get_text()
        self.league = a_div_lc[3].get_text()
        self.team_home, self.team_guest = self.formating_teams(content.find('h1').get_text())
        self.match_time = int(content.find('p')['class'][2][1:11])

    def formating_teams(self, value):
        teams = re.split(' - ', value)
        team_home = teams[0].strip()
        team_guest = teams[1].strip()
        return team_home, team_guest

    def show_match(self):
        print('Sport:', self.sport)
        print('Country:', self.country)
        print('League:', self.league)
        print('Teams:', self.team_home, ' - ', self.team_guest)
        print('Time:', strftime("%b %d %Y %H:%M:%S", gmtime(self.match_time)))
        print('URL: ', self.match_url)
        self.match_result.show_result()
        self.match_ratio.show_ratious()
