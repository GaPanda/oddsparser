# -*- coding: utf-8 -*-

import requests
import re
from urllib.request import unquote

user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/62.0.3202.94 YaBrowser/17.11.1.990 Yowser/2.5 Safari/537.36'


def page_request(url):
    headers = {'referer': url,
               'user-agent': user_agent}
    response = requests.get(url, headers=headers)
    return response.text


def match_data_request(url):
    html = page_request(url)
    xhash = unquote(re.search('"xhash":"(.+?)"', html).group(1))
    id_match = re.search('"id":"(.+?)"', html).group(1)
    id_sport = re.search('"sportId":(.+?)', html).group(1)
    id_version = re.search('"versionId":(.+?)', html).group(1)
    return id_version, id_sport, id_match, xhash


def json_request(url, url_ending):
    feed_url = 'http://fb.oddsportal.com/feed/'
    headers = {'referer': url,
               'user-agent': user_agent}
    json_url = feed_url + url_ending
    response = requests.get(json_url, headers=headers)
    return response.text
