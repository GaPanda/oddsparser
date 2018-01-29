import re
from urllib.request import urlopen, unquote, Request

#Тут нужно еще допилить запросики для результатов :)

class PortalRequest:
    def __init__(self, match_url):
        self.match_url = match_url
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 YaBrowser/17.11.1.990 Yowser/2.5 Safari/537.36'

    def match_request(self):
        request = Request(self.match_url)
        request.add_header('referer', self.match_url)
        request.add_header('user-agent', self.user_agent)
        self.html = urlopen(request).read().decode('utf-8')
        return self.html

    def ratio_request(self):
        xhash = re.search('"xhash":"(.+?)"', self.html).group(1)
        id_match = re.search('"id":"(.+?)"', self.html).group(1)
        id_sport = re.search('"sportId":(.+?)', self.html).group(1)
        id_version = re.search('"versionId":(.+?)', self.html).group(1)
        xhash_decode = unquote(xhash)
        request = Request('http://fb.oddsportal.com/feed/match/{0}-{1}-{2}-1-2-{3}.dat'.format(id_version, id_sport, id_match, xhash_decode))
        request.add_header('referer', self.match_url)
        request.add_header('user-agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 YaBrowser/17.11.1.990 Yowser/2.5 Safari/537.36')
        json_callback = urlopen(request).read().decode('utf-8')
        return json_callback
