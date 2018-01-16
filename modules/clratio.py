#-*- coding: utf-8 -*-

from threading import Thread
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class MatchRatio(Thread):

    def __init__(self, match_url, browser, login, passw):
        super(MatchRatio, self).__init__()
        self.match_url = match_url
        self.bookmakers = []
        self.login = login
        self.passw = passw
        self.driver = browser

    def isfloat(self, value):
        try:
            float(value)
            return True
        except:
            return False

    def try_to_connect(self):
        try:
            self.open_connection()
            self.logging_in(self.login, self.passw)
            print("[INFO] Успешный вход!")
        except Exception as err:
            print("[WARNING]", err.args[0])

    def open_connection(self):
        print("[INFO] Загрузка страницы oddsportal.com.")
        self.driver.get('http://www.oddsportal.com/login')
        self.driver.set_window_size(1024, 768)

    def logging_in(self, login, passw):
        '''Login in oddsportal.com'''
        try:
            print("[INFO] Вход в личный кабинет.")
            username = self.driver.find_element_by_name('login-username')
            password = self.driver.find_element_by_name('login-password')
            username.send_keys(login)
            password.send_keys(passw)
            password.send_keys('\n')
        except:
            raise Exception('You may be already login in!')

    def close_connection(self):
        self.driver.close()

    def run(self): #Нахождение букмекерский контор и их коэффициентов
        self.try_to_connect()
        self.driver.get(self.match_url)
        rows = self.driver.find_elements_by_class_name('lo')
        self.len_rows = len(rows)
        for row in rows:
            elements = row.find_elements_by_tag_name('td')
            div = elements[0].find_element_by_class_name('l')
            tag_a = div.find_elements_by_tag_name('a')
            name_bookmaker = tag_a[1].text
            ratio_1 = self.ratious(self.driver, elements[1])
            ratio_2 = self.ratious(self.driver, elements[2])
            self.bookmakers.append(Bookmaker(name_bookmaker, ratio_1, ratio_2))
        self.close_connection()

    def ratious(self, driver, element): #Обработка разницы начального и конечного коэффициента
        ratio = ''
        hov = ActionChains(driver).move_to_element(element)
        hov.perform()
        try:
            data_in_the_bubble = driver.find_element_by_xpath("//*[@id='tooltiptext']")
        except:
            ratio = 'Error'
            return ratio
        hover_data = BeautifulSoup(data_in_the_bubble.get_attribute("innerHTML"), "lxml")
        temp_data = hover_data.find_all('strong')
        data = self.correct_ratio(temp_data)
        if len(data) > 1:
            last_ratio = data[0].get_text().strip()
            first_ratio = data[len(data)-1].get_text().strip()
            if self.isfloat(last_ratio) & self.isfloat(first_ratio): #Не обязательное условие
                if (bool(last_ratio) & bool(first_ratio) != False) & (last_ratio < first_ratio):
                    ratio = 'Lower'
                elif (bool(last_ratio) & bool(first_ratio) != False) & (last_ratio > first_ratio):
                    ratio = 'Higher'
                else:
                    ratio = 'Equal'
        else:
            ratio = 'Error'
        return ratio

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

    def correct_ratio(self, value): #Удаление ненужной строки из коэффициентов
        length = len(value)
        if self.isfloat(value[length-1].get_text()):
            return value
        else:
            value.pop(length-1)
            return value

    def print_ratious(self):
        for key in self.bookmakers:
            key.printBookmaker()

class Bookmaker:
    def __init__(self, name_bookmaker, ratio_1, ratio_2):
        self.name_bookmaker = name_bookmaker
        self.ratio_1 = ratio_1
        self.ratio_2 = ratio_2

    def printBookmaker(self):
        print('Bookmaker: ', self.name_bookmaker)
        print('1: ', self.ratio_1)
        print('2: ', self.ratio_2)

    def check_ratio_errors(self):
        if self.ratio_1 == 'Higher' and self.ratio_2 == 'Higher':
            return False
        else:
            return True

    def returnRatio(self, result):
        if result == '1':
            if self.check_ratio_errors() and (self.ratio_1 == 'Higher' or self.ratio_1 == 'Lower'):
                return self.ratio_1
            else:
                return
        elif result == '2':
            if self.check_ratio_errors() and (self.ratio_2 == 'Higher' or self.ratio_2 == 'Lower'):
                return self.ratio_2
            else:
                return
        else:
            print('Error with result!')
