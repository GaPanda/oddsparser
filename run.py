#-*- coding: utf-8 -*-

from threading import Thread
from bs4 import BeautifulSoup
from modules.clmatch import get_page
from modules.clmatch import Match
from modules.clratio import MatchRatio
from modules.clsettings import Settings
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, UnableToSetCookieException


class Process(Thread):
    def __init__(self, phantomjs_path, dcap,
                 login, passw, number_of_history_matches):
        super(Process, self).__init__()
        self.base_url = 'http://www.oddsportal.com'
        self.browser = webdriver.PhantomJS(executable_path = phantomjs_path,
                                           desired_capabilities = dcap,
                                           service_args = ["--load-images=no",
                                                           "--ssl-protocol=any",
                                                           "--ignore-ssl-errors=true"])
        self.login = login
        self.passw = passw
        self.number_of_history_matches = number_of_history_matches
        self.matches_home_team = []
        self.matches_guest_team = []

    def try_to_connect(self, cookies):
        try:
            print("[INFO] Проверка подключения к oddsportal.com")
            self.open_connection(cookies)
            result = self.check_connection()
            if result is True:
                self.check_loggin_in()
            else:
                raise NoSuchElementException
        except NoSuchElementException:
            raise NoSuchElementException
        except NameError:
            self.logging_in()

    def open_connection(self, cookies):
        try:
            self.browser.get(self.base_url)
            if cookies is not None:
                for cookie in cookies:
                    #If I dont make sure the domain of the cookie starts with a . i get the following error:
                    #WebDriverException: Message: {"errorMessage":"Unable to set Cookie", ...
                    if cookie['domain'][0] != '.':
                        cookie['domain'] = '.' + cookie['domain']
                    self.browser.add_cookie(cookie)
            self.browser.get(self.base_url)
            self.browser.set_window_size(1024, 768)
        except UnableToSetCookieException:
            self.browser.get(self.base_url)

    def logging_in(self):
        print("[INFO] Вход в личный кабинет.")
        self.browser.get(self.base_url + '/login')
        username = self.browser.find_element_by_name('login-username')
        password = self.browser.find_element_by_name('login-password')
        username.send_keys(self.login)
        password.send_keys(self.passw)
        password.send_keys('\n')
        print("[INFO] Успешный вход!")

    def check_connection(self):
        try:
            self.browser.find_element_by_xpath('//*[@id="user-header-r2"]')
            return True
        except:
            return False

    def check_loggin_in(self):
        try:
            login = self.browser.find_element_by_xpath('//*[@id="user-header-r2"]/ul/li[5]/a')
            if login.text.strip() != self.login:
                #Тут поидее надо написать вход под другим логином, но мне влом)
                print("Logins are not equal :)")
                return False
            else:
                print("[INFO] Успешный вход из cookies!")
                return True
        except:
            raise NameError

    def return_cookies(self):
        self.browser.get(self.base_url)
        cookies = self.browser.get_cookies()
        return cookies

    def close_connection(self):
        self.browser.close()

    def check_empty_table(self, tag):
        return tag.has_attr('class') and tag.has_attr('xeid') and tag.name == 'tr'

    def check_tables_for_teams(self, tag): #Проверка на наличие таблицы с командами
        print("[INFO] Проверка на наличие таблицы с командами.")
        if tag != None: return True
        else: return False

    def check_for_n_matches(self, tag):
        print("[INFO] Проверка количества матчей в таблице Results.")
        if(len(tag)) < self.number_of_history_matches:
            return True

    def find_matches(self, html): #Поиск 10 предыдущих матчей команды
        history_matches = []
        soup = BeautifulSoup(html, 'lxml')
        table_with_matches = soup.find('table', class_='table-main')
        rows = table_with_matches.find_all(self.check_empty_table)
        if self.check_for_n_matches(rows):
            return False
        else:
            for i in range(0, self.number_of_history_matches):
                match_time_td = rows[i].find('td', class_='table-time')
                match_time = match_time_td['class'][2][1:11]
                match_link = rows[i].find('td', class_='name table-participant').a.get('href')
                history_matches.append({
                    'Time': match_time,
                    'Link': base_url + match_link
                    })
        return history_matches

    def find_table_of_history_matches(self, team_url, team_sport, team_country, team_name):
        teams = []
        history_matches = []
        soup = BeautifulSoup(get_page(team_url), 'lxml')
        table_with_teams = soup.find('table', class_='sortable table-main')
        if self.check_tables_for_teams(table_with_teams):
            rows = table_with_teams.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                teams.append({
                    'team': cols[0].get_text().strip(),
                    'link': cols[0].a.get('href').strip(),
                    'country': cols[2].get_text().strip(),
                    'sport': cols[1].get_text().strip(),
                    })
            for team in teams:
                if team['team'] is team_name and team['country'] is team_country and team['sport'] is team_sport:
                    history_matches = find_matches(get_page(base_url + team['Link']))
                    break
                else:
                    raise Exception('No history matches for team:', team_name)
        else:
            history_matches = find_matches(get_page(team_url))
        return history_matches

    def print_history_matches(self, matches_home_team, matches_guest_team):
        for i in range(0, self.number_of_history_matches):
            self.matches_home_team[i].short_show_match2()
            print(' ', end = '')
            self.matches_guest_team[i].short_show_match2()
            print('\n')

    def thread_parse_history_matches(self, matches):
        parsed_matches = []
        for key in matches:
            parsed_block = []
            match_node = Match(key['Link'])
            parsed_block.append(match_node)
            parsed_matches.append(parsed_block)
            match_node.start()
            match_ratio.start()
            return parsed_matches

    def thread_matches_join(parsed_matches):
        for key in parsed_matches:
            key[0].join()
            key[1].join()
            key[0].short_show_match()
            key[0].add_ratio(key[1])
            key[0].show_match()
            key[0].show_ratio()

    def run(self, match_url):
        self.match_url = match_url
        self.match_node = Match(self.match_url)
        self.match_node.start()
        match_ratio = MatchRatio(match_url, self.browser, login, passw)
        match_ratio.start()
        matches_home_team = self.find_table_of_history_matches(match_node.team_home_url, match_node.sport,
                                                          match_node.country, match_node.team_home,
                                                          number_of_history_matches)
        matches_guest_team = self.find_table_of_history_matches(match_node.team_guest_url, match_node.sport,
                                                           match_node.country, match_node.team_guest,
                                                           number_of_history_matches)
        self.match_node.join()
        match_ratio.join()
        self.match_node.add_ratio(match_ratio)
        self.match_node.show_match()
        self.match_node.show_ratio()

        if (matches_home_team is not False) & (matches_guest_team is not False):
            home_m = thread_parse_history_matches(matches_home_team, browser, login, passw)
            guest_m = thread_parse_history_matches(matches_guest_team, browser, login, passw)
            thread_matches_join(home_m)
            thread_matches_join(guest_m)
        else:
            print("[ERROR] Не найдено", number_of_history_matches, "матчей в таблице Results у одной из команд.")
        #try:
        #    print('Finnaly:')
        #    print_history_matches(matches_home_team, matches_guest_team)
        #except Exception as err:
        #    print('[ERROR]', err.args[0])


def main():
    settings = Settings()
    settings.arg_parse()
    settings.dcap_init()
    process = Process(settings.phanjs_path, settings.dcap,
                      settings.login, settings.passw,
                      settings.number_of_history_matches)
    try:
        process.try_to_connect(settings.load_cookies())
        #match_url = input('[INFO] Введите URL матча: ')
        #process.run(match_url)
        settings.save_cookies(process.return_cookies())
        settings.time_count()
    except NoSuchElementException:
        print("[ERROR] Нету доступа к oddsportal, проверь VPN!")

if __name__ == '__main__':
    main()
    input("Press Enter to continue...")
