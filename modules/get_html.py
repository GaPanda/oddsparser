from urllib.request import urlopen

def get_page(url): 
    #Получение HTML кода страницы
    page = urlopen(url)
    return page.read()
