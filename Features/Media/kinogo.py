from .Media import *
import requests
from bs4 import BeautifulSoup as BS
import os
from ..Command import Callback, Response
################################################################################
def findPage(name):
    query = name + ' site:kinogo.by'
    responce = requests.get(f'https://www.google.ru/search?&q={query}&lr=lang_ru&lang=ru')
    page = BS(responce.content, 'html.parser')
    link = page.select_one('.ZINbbc.xpd.O9g5cc.uUPGi>.kCrYT>a')
    title = page.select_one('.ZINbbc.xpd.O9g5cc.uUPGi .BNeawe.vvjwJb.AP7Wnd').text.split(' смотреть')[0].strip()
    return (link['href'][7:].split('&')[0], title) if link else None

def getFilm(url):
    id = url[18:].split('-')[0].split(',')[-1]
    url = f'https://kinogo.la/engine/ajax/cdn_download.php?news_id={id}'
    responce = requests.get(url)

    page = BS(responce.content, 'html.parser')
    elems = page.children
    for elem in elems:
        if elem == '\n': continue
        spans = elem.find_all('span')
        audio = spans[1].text
        if 'Оригинальная дорожка' in audio or 'Полное дублирование' in audio or 'LostFilm' in audio:
            return elem.ul.li.a['href']
    return None

def getSerial(url):
    id = url[18:].split('-')[0].split(',')[-1]
    url = f'https://kinogo.la/engine/ajax/cdn_download.php?news_id={id}'
    responce = requests.get(url)
    page = BS(responce.content, 'html.parser')
    elems = page.children
    n = len(page.select('.cdn_download_season')) or 1
    seasons = [None]*n
    current_season = n-1
    for elem in elems:
        if elem == '\n': continue
        if elem['class'][0] == 'cdn_download_season':
            current_season = int(elem.text.split(' ')[0])-1
            seasons[current_season] = {}
            continue
        spans = elem.find_all('span')
        if not spans: break
        audio = spans[2].text
        if audio in ['Оригинальная дорожка', 'Полное дублирование', 'LostFilm']:
            num = int(spans[0].text.split(' ')[0])-1
            seasons[current_season][num] = {'href': elem.ul.li.a['href'], 'title': f'{current_season+1} сезон {num+1} серия'}

    new_seasons = []
    for dict_s in seasons:
        season = [None]*(max(dict_s.keys())+1)
        for i, value in dict_s.items():
            season[i] = value
        season = list(filter(None, season))
        new_seasons.append(season)

    return new_seasons

def startFilm(url, title):
    os.system(f'lxterminal --command="vlc {url} -f --meta-title=\\"{title}\\" "')

def startSerial(seasons, name):
    for season in seasons:
        for series in season:
            print(series)
            href = series['href']
            title = name + ' ' + series['title']
            os.system(f'lxterminal --command="vlc --playlist-enqueue {href} --meta-title=\\"{title}\\" "')

def film(params):
    name = params.get('text')
    if name:
        url, title = findPage(name)
        url = getFilm(url)
        if url:
            startFilm(url, title)
            voice = text = 'Включаю'
        else:
            voice = text = 'Не могу найти фильм'
    else:
        voice = text = 'Какой фильм включить?'
        callback = kinogo_film_cb
        return Response(text = text, voice = voice, callback = callback)
    return Response(text = text, voice = voice)

def start_film(params):
    name = params.get('text')
    voice = text = 'Не могу найти фильм'
    if name:
        url, title = findPage(name)
        url = getFilm(url)
        if url:
            startFilm(url, title)
            voice = text = 'Включаю'
    return Response(text = text, voice = voice)

def serial(params):
    name = params.get('text')
    if name:
        url, title = findPage(name)
        seasons = getSerial(url)
        if url:
            startSerial(seasons, title)
            voice = text = 'Включаю'
        else:
            voice = text = 'Не могу найти'
    else:
        voice = text = 'Какой сериал включить?'
        callback = kinogo_serial_cb
        return Response(text = text, voice = voice, callback = callback)
    return Response(text = text, voice = voice)

def start_serial(params):
    name = params.get('text')
    voice = text = 'Не могу найти сериал'
    if name:
        url, title = findPage(name)
        seasons = getSerial(url)
        if url:
            startSerial(url, title)
            voice = text = 'Включаю'
    return Response(text = text, voice = voice)

kinogo_film_cb = Callback(['$text',])
kinogo_film_cb.setStart(start_film)

patterns = ['* включ* фильм $text', '* включ* фильм*']
kinogo_film = Media('KinogoFilm', {}, patterns)
kinogo_film.setStart(film)


kinogo_serial_cb = Callback(['$text',])
kinogo_serial_cb.setStart(start_serial)

patterns = ['* включ* сериал $text', '* включ* сериал*']
kinogo_serial = Media('KinogoSerial', {}, patterns)
kinogo_serial.setStart(serial)
