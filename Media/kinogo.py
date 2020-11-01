from .Film import *
import requests
from bs4 import BeautifulSoup as BS
import os
import Command
################################################################################
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
    title = page.select_one('h1')
    return (url['href'], title.text) if url else None

def startFilm(url, title):
    os.system(f'lxterminal --command="vlc {url} -f --meta-title="{title}" "')

def main(params):
    name = params.get('text')
    if name:
        url, title = extractUrl(findFilm(name))
        if url:
            startFilm(url, title.replace(' ', ''))
            voice = text = 'Включаю'
        else:
            voice = text = 'Не могу найти фильм'
        type = 'simple'
    else:
        voice = text = 'Какой фильм включить?'
        type = 'question'
        callback = kinogo_cb
        return {
            'type': type,
            'text': text,
            'voice': voice,
            'callback': callback,
        }
    return {
        'type': type,
        'text': text,
        'voice': voice,
    }

def start(params):
    name = params.get('text')
    voice = text = 'Не могу найти фильм'
    if name:
        if url:= extractUrl(findFilm(name)):
            startFilm(url)
            voice = text = 'Включаю'
    return {
        'type': 'simple',
        'text': text,
        'voice': voice,
    }

kinogo_cb = Command.Callback(['$text',])
kinogo_cb.setStart(start)

patterns = ['* включ* фильм $text', '* включ* фильм*']
kinogo = Film('KinogoPlayer', {}, patterns)
kinogo.setStart(main)
