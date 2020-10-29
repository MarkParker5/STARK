from .film import *
import requests
from bs4 import BeautifulSoup as BS
import os

################################################################################
def method(params):
    def findFilm(name):
        query = name + ' site:kinogo.by'
        responce = requests.get(f'https://www.google.ru/search?&q={query}&lr=lang_ru&lang=ru')
        page = BS(responce.content, 'html.parser')
        link = page.select_one('.ZINbbc.xpd.O9g5cc.uUPGi>.kCrYT>a')
        return link['href'][7:].split('&')[0] if link else None

    def extractUrl(url):
        responce = requests.get(url)
        page = BS(responce.content, 'html.parser')
        url = page.select_one('div[style="padding:22px; float:left; margin-left: 30px;"]>a[download]:last-child')
        return url['href'] if url else None

    def start(url):
        os.system(f'lxterminal --command="vlc {url}"')

    name = params.get('text')
    print(name)
    if name:
        if url:= extractUrl(findFilm(name)):
            start(url)
            voice = text = 'Включаю'
        else:
            voice = text = 'Не могу найти фильм'
    else:
        voice = text = 'Какой фильм включить?'

    return {
        'type': 'simple',
        'text': text,
        'voice': voice,
    }

patterns = ['* включ* фильм $text', '* включ* фильм*']
subpatterns = ['$text',]
kinogo = film('KinogoPlayer', {}, patterns, subpatterns)
kinogo.setStart(method)
