# -*- coding: utf-8 -*-

import re
import json
from threading import Thread
from bs4 import BeautifulSoup
import core.request


class Result(Thread):
    def __init__(self, match_url):
        super(Result, self).__init__()
        self.match_url = match_url
        self.result = None
        self.started_status = False
        self.finished_status = False
        self.canceled_status = False
        self.id_sport = None
        self.id_match = None
        self.xhash = None

    def add_keys(self, xhash, id_sport, id_match):
        self.id_sport = id_sport
        self.id_match = id_match
        self.xhash = xhash

    def result_request(self):
        if self.xhash is None and self.id_sport is None and self.id_match is None:
            id_version, id_sport, id_match, xhash = core.request.match_data_request(self.match_url)
            url_ending = 'postmatchscore/{0}-{1}-{2}.dat'.format(id_sport, id_match, xhash)
        else:
            url_ending = 'postmatchscore/{0}-{1}-{2}.dat'.format(self.id_sport, self.id_match, self.xhash)
        json = core.request.json_request(self.match_url, url_ending)
        return json

    def run(self):
        json_request = self.result_request()
        json_string = re.search('[{](.+)[}]', json_request).group(0)
        data = json.loads(json_string)
        d = data.get('d')
        result = d.get('result')
        self.started_status = bool(d.get('isStarted'))
        self.finished_status = bool(d.get('isFinished'))
        if result:
            soup = BeautifulSoup(result, 'lxml')
            self.string_result = soup.find('p', class_='result').get_text()[13:]
            self.result = self.formating_results(result)
        else:
            self.string_result = "Not started yet."

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
            result = None
        return result

    def show_result(self):
        print("Result:", self.result, "(" + self.string_result + ")")
