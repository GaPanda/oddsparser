#-*- coding: utf-8 -*-

from modules.clbookmaker import Bookmaker

class MatchRatio:
    def __init__(self, match_url, portal_request):
        super(MatchRatio, self).__init__()
        self.match_url = match_url
        self.portal_request = portal_request
        self.bookmakers = []

    def run(self): #Нахождение букмекерский контор и их коэффициентов
        json = self.portal_request.ratio_request()
        print(json)

    def ratious(self): #Обработка разницы начального и конечного коэффициента
        pass

    def count_ratio(self, result):
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
