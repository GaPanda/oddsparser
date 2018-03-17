# -*- coding: utf-8 -*-

import re
import json
import logging
from urllib.request import urlopen, Request, unquote
from threading import Thread
from bs4 import BeautifulSoup

user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 YaBrowser/17.11.1.990 Yowser/2.5 Safari/537.36'
feed_url = 'http://fb.oddsportal.com/feed/'


class Result(Thread):
    def __init__(self, match_url):
        super(Result, self).__init__()
        self.match_url = match_url
        self.result = None
        self.started_status = False
        self.finished_status = False
        self.canceled_status = False

    def add_keys(self, xhash, id_sport, id_match):
        self.id_sport = id_sport
        self.id_match = id_match
        self.xhash = xhash

    def match_data_request(self):
        request = Request(self.match_url)
        request.add_header('referer', self.match_url)
        request.add_header('user-agent', user_agent)
        html = urlopen(request).read().decode('utf-8')
        self.xhash = unquote(re.search('"xhash":"(.+?)"', html).group(1))
        self.id_match = re.search('"id":"(.+?)"', html).group(1)
        self.id_sport = re.search('"sportId":(.+?)', html).group(1)

    def result_request(self, xhash, id_sport, id_match):
        request = Request(feed_url + 'postmatchscore/{0}-{1}-{2}.dat'.format(id_sport,
                                                                             id_match,
                                                                             xhash))
        request.add_header('referer', self.match_url)
        request.add_header('user-agent', user_agent)
        value = urlopen(request).read().decode('utf-8')
        return value

    def run(self):
        if self.xhash is None and self.id_sport is None and self.id_match is None:
            self.match_data_request()
            json_request = self.result_request(self.xhash, self.id_sport, self.id_match)
        else:
            json_request = self.result_request(self.xhash, self.id_sport, self.id_match)
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

    # Необходимо доделать до ума!!!!!!!
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

    def logging_result(self):
        logging.info("Result:" + str(self.result) + "(" + str(self.string_result) + ")")

    def print_result(self):
        print("Result:", self.result, "(" + self.string_result + ")")
