# -*- coding: utf-8 -*-

import json
import re
from threading import Thread
from enum import Enum, unique
import core.request


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
        self.ratio.sort(key=lambda i: i[2])
        if len(self.ratio) > 1:
            self.first = float(self.ratio[0][0])
            self.last = float(self.ratio[-1][0])
            if self.first < self.last:
                self.counted_ratio = Ratio.HIGHER
            elif self.first > self.last:
                self.counted_ratio = Ratio.LOWER
            elif self.first == self.last:
                self.counted_ratio = Ratio.EQUAL
            else:
                self.counted_ratio = Ratio.ERROR
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
    def __init__(self, match_url, ratio_percents):
        super(MatchRatio, self).__init__()
        self.match_url = match_url
        self.ratio_percents = ratio_percents
        self.bookmakers = []
        self.counted_ratio = []
        self.xhash = None
        self.id_sport = None
        self.id_match = None
        self.id_version = None

    def dict_to_list(self, key):
        if type(key).__name__ == "dict":
            return list(key.values())
        else:
            return key

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

    def ratio_request(self):
        if self.xhash is None and self.id_sport is None and self.id_match is None and self.id_version is None:
            id_version, id_sport, id_match, xhash = core.request.match_data_request(self.match_url)
            url_ending = 'match/{0}-{1}-{2}-3-1-{3}.dat'.format(id_version, id_sport, id_match, xhash)
        else:
            url_ending = 'match/{0}-{1}-{2}-3-1-{3}.dat'.format(self.id_version, self.id_sport, self.id_match, self.xhash)
        json = core.request.json_request(self.match_url, url_ending)
        return json

    def run(self):
        '''Нахождение букмекерский контор и их коэффициентов'''
        json_request = self.ratio_request()
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
                history_ratious.append({"bookmaker": bkey,
                                        "token": key,
                                        "ratio": ratio})
        history_ratious.extend(history_ratious_2)
        self.add_counted_ratio(outcomeid_sorted)
        self.ratious(history_ratious, array_tokens)
        self.count_all_ratio()
        self.result_counted_ratio()

    def ratious(self, history_ratious, array_tokens):
        for key in self.bookmakers:
            key.add_tokens(array_tokens)
            id_b = key.get_id()
            for x in history_ratious:
                if x["bookmaker"] == id_b:
                    key.add_ratio(x["token"], x["ratio"])
            key.count_ratio()

    def count_all_ratio(self):  # Подсчет значений
        for key in self.bookmakers:
            if key.status is True:
                array_nodes = key.return_ratious()
                for array_node in array_nodes:
                    token = array_node.token
                    counted_ratio = array_node.counted_ratio
                    if counted_ratio == Ratio.HIGHER:
                        self.iter_counted_ratio(token, Ratio.HIGHER)
                    elif counted_ratio == Ratio.LOWER:
                        self.iter_counted_ratio(token, Ratio.LOWER)
                    elif counted_ratio == Ratio.EQUAL:
                        self.iter_counted_ratio(token, Ratio.EQUAL)
                    else:
                        self.iter_counted_ratio(token, Ratio.ERROR)
            else:
                continue

    def result_counted_ratio(self):
        for key in self.counted_ratio:
            if (key['counts'][Ratio.HIGHER] / key['counts']['total'] * 100) > self.ratio_percents:
                key['result'] = Ratio.HIGHER
            elif (key['counts'][Ratio.LOWER] / key['counts']['total'] * 100) > self.ratio_percents:
                key['result'] = Ratio.LOWER
            elif (key['counts'][Ratio.EQUAL] / key['counts']['total'] * 100) > self.ratio_percents:
                key['result'] = Ratio.EQUAL
            else:
                key['result'] = Ratio.ERROR

    def show_ratious(self):
        if len(self.counted_ratio) == 2:
            names = ['1:', '2:']
        else:
            names = ['1:', 'X:', '2:']
        i = 0
        for key in self.counted_ratio:
            print(names[i], key['result'].value)
            print('[Higher:', key['counts'][Ratio.HIGHER],
                  "; Lower:", key['counts'][Ratio.LOWER], end=' ')
            print('; Equal:', key['counts'][Ratio.EQUAL],
                  "; Error:", key['counts'][Ratio.ERROR],
                  "; Total", key['counts']['total'], ']')
            i += 1
        # for key in self.bookmakers:
        #    key.print_bookmaker()
