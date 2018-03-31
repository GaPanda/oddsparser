from threading import Thread
from core.match import Match
from core.ratio import MatchRatio
from core.result import Result
from core.request import match_data_request


class MatchStruct(Thread):
    def __init__(self, url, ratio_percents):
        super(MatchStruct, self).__init__()
        self.url = url
        self.match = Match(url)
        self.result = Result(url)
        self.ratio = MatchRatio(url, ratio_percents)
        self.daemon = True

    def run(self):
        self.match.start()
        xhash, id_sport, id_match, id_version = match_data_request(self.url)
        self.ratio.add_keys(xhash, id_sport, id_match, id_version)
        self.result.add_keys(xhash, id_sport, id_match)
        self.ratio.start()
        self.result.start()

    def print_match(self):
        self.match.show_match()
        self.result.show_result()
        self.ratio.show_ratious()
