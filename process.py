# -*- coding: utf-8 -*-

from time import time
from threading import Thread
from argparse import ArgumentParser
from core.struct import MatchStruct
from core.history import HistoryMatches


class Process(Thread):
    def __init__(self, number_of_history_matches, ratio_percents, match_url):
        super(Process, self).__init__()
        self.match_url = match_url
        self.number_of_history_matches = number_of_history_matches
        self.ratio_percents = ratio_percents
        self.match_node = MatchStruct(match_url, ratio_percents)
        self.home_matches = []
        self.guest_matches = []
        self.deamon = True

    def parse_history_matches(self, node):
        home_matches = HistoryMatches(self.number_of_history_matches,
                                      self.ratio_percents,
                                      node.sport, node.country,
                                      node.team_home, node.match_time)
        home_matches.start()
        guest_matches = HistoryMatches(self.number_of_history_matches,
                                       self.ratio_percents,
                                       node.sport, node.country,
                                       node.team_guest, node.match_time)
        guest_matches.start()
        return home_matches, guest_matches

    def print_history_matches(self, array):
        i = 1
        for key in array:
            key = self.join_threads(key)
            print("-----------------------------------------------------------")
            print("Матч №" + str(i))
            key.show_match()
            i += 1

    def print_process(self):
        if (len(self.home_matches) != 0) & (len(self.guest_matches) != 0):
            print('\nМатчи домашней команды:')
            self.print_history_matches(self.home_matches)
            print('\nМатчи гостевой команды:')
            self.print_history_matches(self.guest_matches)
        else:
            print("[ERROR] Не найдено матчей у одной из команд.")

    def run(self):
        try:
            self.match_node.run()
            self.match_node.print_match()
            if self.match_node.match.sport == "Basketball":
                self.home_matches, self.guest_matches = self.parse_history_matches(self.match_node.match)
            else:
                print("[WARNING] Пока что только баскетбол :(")
        except UnicodeDecodeError:
            print("[ERROR] Не удается подключиться к oddsportal.")


def main(num):
    number_of_history_matches = num
    ratio_percents = 50
    print("[INFO] Количество матчей из истории:", number_of_history_matches)
    match_url = input('[INFO] Введите URL матча: ')
    start_time = time()
    process = Process(number_of_history_matches, ratio_percents, match_url)
    process.start()
    process.join()
    process.print_process()
    end_time = time() - start_time
    print('[INFO] Программа завершена за: {0:.2f} секунд.'.format(end_time))


if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-n", "--number", default=6)
    args = vars(arg_parser.parse_args())
    num = int(args["number"])
    main(num)
    input("Press Enter to continue...")
