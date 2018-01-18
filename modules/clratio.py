#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from modules.clbookmaker import Bookmaker

class MatchRatio:
    def __init__(self, match_url, browser, handle):
        super(MatchRatio, self).__init__()
        self.match_url = match_url
        self.bookmakers = []
        self.login = login
        self.passw = passw
        self.driver = browser


    def run(self): #Нахождение букмекерский контор и их коэффициентов
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
