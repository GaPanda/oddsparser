#-*- coding: utf-8 -*-

import json
import re
from modules.clbookmaker import Bookmaker

class MatchRatio:
    def __init__(self, match_url, portal_request):
        super(MatchRatio, self).__init__()
        self.match_url = match_url
        self.portal_request = portal_request
        self.bookmakers = []

    def dict_to_list(self, elem):
        if type(elem).__name__ == "dict":
            return list(elem.values())
        else:
            return elem

    def run(self): #Нахождение букмекерский контор и их коэффициентов
        json_callback = self.portal_request.ratio_request()
        json_string = re.search('[{](.+)[}]', json_callback).group(0)
        data = json.loads(json_string)
        oddsdata = data.get('d').get('oddsdata')
        back = oddsdata.get('back')
        array = list(back.values())
        outcomeid = self.dict_to_list(array[0].get('OutcomeID'))
        odds = array[0].get('odds')
        change_time = array[0].get('change_time')
        history_ratious_2 = []
        for key in odds:
            odd = self.dict_to_list(odds.get(key))
            time = self.dict_to_list(change_time.get(key))
            for i in range(0, len(odd)):
                history_ratious_2.append({"bookmaker": key,
                                          "token": outcomeid[i],
                                          "ratio": [[str(odd[i]), 0, time[i]]]})
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
        self.ratious(history_ratious, array_tokens)

    def ratious(self, history_ratious, array_tokens): #Добавление в класс значений
        for key in self.bookmakers:
            key.add_tokens(array_tokens)
            id_b = key.get_id()
            for x in history_ratious:
                if x["bookmaker"] == id_b:
                    key.add_ratio(x["token"], x["ratio"])

    def count_ratio(self, result): #Подсчет значений
        procents = 70
        lower, higher, error = [], [], []
        for key in self.bookmakers:
            ratio = key.returnRatio(result)
            if ratio == 'Higher': higher.append(ratio)
            elif ratio == 'Lower': lower.append(ratio)
            elif ratio == 'Error': error.append(ratio)
            else: continue
        len_lower = len(lower)
        len_higher = len(higher)
        if (len_lower / self.len_rows * 100) > procents:
            final_ratio = 'Lower'
        elif (len_higher / self.len_rows * 100) > procents:
            final_ratio = 'Higher'
        else:
            final_ratio = 'Error'
        counts = [len(lower), len(higher), len(error), self.len_rows, final_ratio]
        return counts

    def print_ratious(self):
        for key in self.bookmakers:
            key.print_bookmaker()
