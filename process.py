# -*- coding: utf-8 -*-

from time import time
from threading import Thread
from argparse import ArgumentParser
from core.match import Match
from core.ratio import MatchRatio
from core.result import Result
from core.history import HistoryMatches


class Process(Thread):
    def __init__(self, number_of_history_matches, ratio_percents, match_url):
        super(Process, self).__init__()
        self.match_url = match_url
        self.number_of_history_matches = number_of_history_matches
        self.ratio_percents = ratio_percents
        self.match = None
        self.home_matches = []
        self.guest_matches = []
        self.status_end = False

    def start_threads(self, url):
        node = Match(url)
        node_ratio = MatchRatio(url, self.ratio_percents)
        node_result = Result(url)
        node.start()
        node.join()
        xhash, id_sport, id_match, id_version = node.return_keys()
        node_ratio.add_keys(xhash, id_sport, id_match, id_version)
        node_result.add_keys(xhash, id_sport, id_match)
        node_ratio.start()
        node_result.start()
        node.add_data(node_ratio, node_result)
        return node

    def join_threads(self, node):
        node.match_ratio.join()
        node.match_result.join()
        return node

    def parse_history_matches(self, node):
        home_matches = HistoryMatches(self.number_of_history_matches,
                                      node.sport, node.country,
                                      node.team_home, node.match_time)
        home_matches.start()
        guest_matches = HistoryMatches(self.number_of_history_matches,
                                       node.sport, node.country,
                                       node.team_guest, node.match_time)
        guest_matches.start()
        home_matches.join()
        guest_matches.join()
        return home_matches, guest_matches

    def print_history_matches(self, array):
        i = 1
        for key in array:
            key = self.join_threads(key)
            print("-----------------------------------------------------------")
            print("Матч №" + str(i))
            key.show_match()
            i += 1

    def run(self):
        try:
            node = self.start_threads(self.match_url)
            self.match = self.join_threads(node)
            self.match.show_match()
            if self.match.sport == "Basketball":
                home, guest = self.parse_history_matches(node)
                if (len(home.matches_urls) != 0) & (len(guest.matches_urls) != 0):
                    i = 0
                    for matches in home.matches_urls, guest.matches_urls:
                        for key in matches:
                            history_node = self.start_threads(key)
                            if i == 0:
                                self.home_matches.append(history_node)
                            elif i == 1:
                                self.guest_matches.append(history_node)
                        i += 1
                    self.status_end = True
                    print('\nМатчи домашней команды:')
                    self.print_history_matches(self.home_matches)
                    print('\nМатчи гостевой команды:')
                    self.print_history_matches(self.guest_matches)
                else:
                    print("[ERROR] Не найдено матчей у одной из команд.")
            else:
                print("[WARNING] Пока что только баскетбол :(")
        except UnicodeDecodeError:
            print("[ERROR] Не удается подключиться к oddsportal.")
        except:
            print("[ERROR] Что-то пошло не так")


def main(num):
    number_of_history_matches = num
    ratio_percents = 50
    print("[INFO] Количество матчей из истории:", number_of_history_matches)
    match_url = input('[INFO] Введите URL матча: ')
    start_time = time()
    process = Process(number_of_history_matches, ratio_percents, match_url)
    process.run()
    end_time = time() - start_time
    print('[INFO] Программа завершена за: {0:.2f} секунд.'.format(end_time))


if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-n", "--number", default=6)
    args = vars(arg_parser.parse_args())
    num = int(args["number"])
    main(num)
    input("Press Enter to continue...")
