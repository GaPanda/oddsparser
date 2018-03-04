#-*- coding: utf-8 -*-

import json
import re
from urllib.request import urlopen, unquote, Request
from threading import Thread
from enum import Enum, unique

user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 YaBrowser/17.11.1.990 Yowser/2.5 Safari/537.36'
feed_url = 'http://fb.oddsportal.com/feed/'

@unique
class Ratio(Enum):
    HIGHER = "Higher"
    LOWER = "Lower"
    EQUAL = "Equal"
    ERROR = "Error"

class Token:
    def __init__(self, index, token):
        self.index = index
        self.token = token
        self.ratio = []
        self.counted_ratio = Ratio.ERROR

    def add_ratio(self, ratio):
        self.ratio.extend(ratio)

    def count_token(self):
        self.ratio.sort(key = lambda i: i[2])
        if len(self.ratio) > 1:
            self.first = float(self.ratio[0][0])
            self.last = float(self.ratio[-1][0])
            if self.first < self.last: self.counted_ratio = Ratio.HIGHER
            elif self.first > self.last: self.counted_ratio = Ratio.LOWER
            elif self.first == self.last: self.counted_ratio = Ratio.EQUAL
            else: self.counted_ratio = Ratio.ERROR
        else:
            self.counted_ratio = Ratio.ERROR

    def print_token(self):
        print("Index:", self.index)
        print("Ratio:", self.ratio)
        print("Token:", self.token)
        print("First:", self.first, "Last:", self.last)
        print("Counted ratio:", self.counted_ratio)

class Bookmaker:
    def __init__(self, id_bookmaker, status):
        self.id_bookmaker = id_bookmaker
        self.status = status
        self.ratious = []

    def add_tokens(self, array):
        for key in array:
            index = array.index(key)
            self.ratious.append(Token(index, key))

    def add_ratio(self, token, ratio):
        for key in self.ratious:
            if key.token == token:
                key.add_ratio(ratio)

    def count_ratio(self):
        for key in self.ratious:
            key.count_token()

    def get_id(self):
        return self.id_bookmaker

    def print_bookmaker(self):
        print('Bookmaker: ', self.id_bookmaker)
        print('Status: ', self.status)
        for key in self.ratious:
            key.print_token()

    def return_ratious(self):
        return self.ratious

class MatchRatio(Thread):
    def __init__(self, match_url):
        super(MatchRatio, self).__init__()
        self.match_url = match_url
        self.bookmakers = []
        self.counted_ratio = []

    def dict_to_list(self, key):
        if type(key).__name__ == "dict": return list(key.values())
        else: return key

    def add_counted_ratio(self, outcomeid):
        for token in outcomeid:
            index = outcomeid.index(token)
            node = {"index": index,
                    "token": token,
                    "result": Ratio.ERROR,
                    "counts": {
                        Ratio.HIGHER: 0,
                        Ratio.LOWER: 0,
                        Ratio.EQUAL: 0,
                        Ratio.ERROR: 0,
                        "total": 0
                    }}
            self.counted_ratio.append(node)

    def add_keys(self, xhash, id_sport, id_match, id_version):
        self.xhash = xhash
        self.id_sport = id_sport
        self.id_match = id_match
        self.id_version = id_version

    def iter_counted_ratio(self, token, ratio):
        for key in self.counted_ratio:
            if key["token"] == token:
                key["counts"][ratio] += 1
                key["counts"]["total"] += 1

    def match_data_request(self):
        request = Request(self.match_url)
        request.add_header('referer', self.match_url)
        request.add_header('user-agent', user_agent)
        html = urlopen(request).read().decode('utf-8')
        self.xhash = unquote(re.search('"xhash":"(.+?)"', html).group(1))
        self.id_match = re.search('"id":"(.+?)"', html).group(1)
        self.id_sport = re.search('"sportId":(.+?)', html).group(1)
        self.id_version = re.search('"versionId":(.+?)', html).group(1)


    def ratio_request(self, xhash, id_sport, id_match, id_version):
        json_request = Request(feed_url + 'match/{0}-{1}-{2}-3-1-{3}.dat'.format(id_version,
                                                                                 id_sport,
                                                                                 id_match,
                                                                                 xhash))
        json_request.add_header('referer', self.match_url)
        json_request.add_header('user-agent', user_agent)
        value = urlopen(json_request).read().decode('utf-8')
        return value

    def run(self): #Нахождение букмекерский контор и их коэффициентов
        if self.xhash is None and self.id_sport is None and self.id_match is None and self.id_version is None:
            self.match_data_request()
            json_request = self.ratio_request(self.xhash, self.id_sport, self.id_match, self.id_version)
        else:
            json_request = self.ratio_request(self.xhash, self.id_sport, self.id_match, self.id_version)
        json_string = re.search('[{](.+)[}]', json_request).group(0)
        data = json.loads(json_string)
        oddsdata = data.get('d').get('oddsdata')
        back = oddsdata.get('back')
        array = list(back.values())
        outcomeid = self.dict_to_list(array[0].get('OutcomeID'))
        outcomeid_sorted = sorted(outcomeid)
        odds = array[0].get('odds')
        change_time = array[0].get('change_time')
        history_ratious_2 = []
        for key in odds:
            odd = self.dict_to_list(odds.get(key))
            time = self.dict_to_list(change_time.get(key))
            for i in range(0, len(odd)):
                history_ratious_2.append({"bookmaker": key,
                                          "token": outcomeid[i],
                                          "ratio": [[odd[i], 0, time[i]]]})
        act = array[0].get('act')
        bookmakers_ids = act.keys()
        for key in bookmakers_ids:
            status = act.get(key)
            self.bookmakers.append(Bookmaker(key, status))
        history = data.get('d').get('history')
        history_back = history.get("back")
        history_ratious = []
        array_tokens = []
        for key in history_back:
            array_tokens.append(key)
            token = history_back.get(key)
            for bkey in token:
                ratio = token.get(bkey)
                history_ratious.append({"bookmaker" : bkey,
                                        "token" : key,
                                        "ratio" : ratio})
        history_ratious.extend(history_ratious_2)
        self.add_counted_ratio(outcomeid_sorted)
        self.ratious(history_ratious, array_tokens)
        self.count_all_ratio()
        self.result_counted_ratio()

    def ratious(self, history_ratious, array_tokens): #Добавление в класс значений
        for key in self.bookmakers:
            key.add_tokens(array_tokens)
            id_b = key.get_id()
            for x in history_ratious:
                if x["bookmaker"] == id_b:
                    key.add_ratio(x["token"], x["ratio"])
            key.count_ratio()

    def check_ratious_errors(self):
        if self.ratio_1 == 'Higher' and self.ratio_2 == 'Higher':  return False
        else: return True

    def count_all_ratio(self): #Подсчет значений
        for key in self.bookmakers:
            if key.status == True:
                array_nodes = key.return_ratious()
                for array_node in array_nodes:
                    token = array_node.token
                    counted_ratio = array_node.counted_ratio
                    if counted_ratio == Ratio.HIGHER: self.iter_counted_ratio(token, Ratio.HIGHER)
                    elif counted_ratio == Ratio.LOWER: self.iter_counted_ratio(token, Ratio.LOWER)
                    elif counted_ratio == Ratio.EQUAL: self.iter_counted_ratio(token, Ratio.EQUAL)
                    else: self.iter_counted_ratio(token, Ratio.ERROR)
            else:
                continue

    def result_counted_ratio(self):
        procents = 60
        for key in self.counted_ratio:
            if (key['counts'][Ratio.HIGHER] / key['counts']['total'] * 100) > procents:
                key['result'] = Ratio.HIGHER
            elif (key['counts'][Ratio.LOWER] / key['counts']['total'] * 100) > procents:
                key['result'] = Ratio.LOWER
            elif (key['counts'][Ratio.EQUAL] / key['counts']['total'] * 100) > procents:
                key['result'] = Ratio.EQUAL
            else:
                key['result'] = Ratio.ERROR

    def print_ratious(self):
        if len(self.counted_ratio) == 2:
            self.print_ratious_2()
        elif len(self.counted_ratio) == 3:
            self.print_ratious_3()
        #for key in self.bookmakers:
        #    key.print_bookmaker()

    def print_ratious_2(self):
        names = ['1:', '2:']
        i = 0
        for key in self.counted_ratio:
            print(names[i], key['result'].value)
            print('[Higher:', key['counts'][Ratio.HIGHER], "; Lower:", key['counts'][Ratio.LOWER], end=' ')
            print('; Equal:', key['counts'][Ratio.EQUAL], "; Error:", key['counts'][Ratio.ERROR], "; Total", key['counts']['total'], ']')
            i += 1

    def print_ratious_3(self):
        names = ['1:','X:' '2:']
        i = 0
        for key in self.counted_ratio:
            print(names[i], key['result'].value)
            print('[Higher:', key['counts'][Ratio.HIGHER], "; Lower:", key['counts'][Ratio.LOWER], end=' ')
            print('; Equal:', key['counts'][Ratio.EQUAL], "; Error:", key['counts'][Ratio.ERROR], "; Total", key['counts']['total'], ']')
            i += 1
