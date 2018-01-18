#-*- coding: utf-8 -*-

import pickle
from time import time
from argparse import ArgumentParser
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class Settings:
    def __init__(self):
        self.start_time = time()
        self.end_time = 0
        self.arg_parser = ArgumentParser()
        self.phanjs_path = r"C:\Users\pingv\Documents\GitHub\oddsparser\phantomjs-2.1.1-windows\bin\phantomjs.exe"

    def time_count(self):
        self.end_time = time() - self.start_time
        print('[INFO] Программа завершена за: ', self.end_time/60, ' мин.')

    def arg_parse(self):
        self.arg_parser.add_argument("-n", "--number", default = 5)
        self.arg_parser.add_argument("-l", "--login", default = "myparsebot")
        self.arg_parser.add_argument("-p", "--password", default = "79213242520")
        args = vars(self.arg_parser.parse_args())
        self.number_of_history_matches = int(args["number"])
        self.login = str(args["login"])
        self.passw = str(args["password"])
        print("[INFO] Количество матчей из истории:", self.number_of_history_matches)
        print("[INFO] Логин:", self.login, "Пароль:", self.passw)

    def dcap_init(self):
        self.dcap = dict(DesiredCapabilities.PHANTOMJS)
        self.dcap["phantomjs.page.settings.userAgent"] = (
             "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0"
        )
    def load_cookies(self):
        print("[INFO] Загрузка cookie файлов.")
        try:
            cookies = pickle.load(open("cookies.pkl", "rb"))
        except FileNotFoundError:
            cookies = None
        return cookies

    def save_cookies(self, cookies):
        pickle.dump(cookies, open("cookies.pkl","wb"))
