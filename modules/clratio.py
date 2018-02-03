#-*- coding: utf-8 -*-

import json
import re
from modules.clbookmaker import Bookmaker
from modules.clbookmaker import Ratio

class MatchRatio:
    def __init__(self, match_url, portal_request):
        super(MatchRatio, self).__init__()
        self.match_url = match_url
        self.portal_request = portal_request
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

    def iter_counted_ratio(self, token, ratio):
        for key in self.counted_ratio:
            if key["token"] == token:
                key["counts"][ratio] += 1
                key["counts"]["total"] += 1

    def run(self): #Нахождение букмекерский контор и их коэффициентов
        json_callback = self.portal_request.ratio_request()
        json_string = re.search('[{](.+)[}]', json_callback).group(0)
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
            array_nodes = key.return_ratious()
            for array_node in array_nodes:
                token = array_node.token
                counted_ratio = array_node.counted_ratio
                if counted_ratio == Ratio.HIGHER: self.iter_counted_ratio(token, Ratio.HIGHER)
                elif counted_ratio == Ratio.LOWER: self.iter_counted_ratio(token, Ratio.LOWER)
                elif counted_ratio == Ratio.EQUAL: self.iter_counted_ratio(token, Ratio.EQUAL)
                else: self.iter_counted_ratio(token, Ratio.ERROR)

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
