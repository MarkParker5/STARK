import requests
from bs4 import BeautifulSoup as BS
import os
from .Media import Media
from ArchieCore import Command, Response

################################################################################

@Command.new(['$text'], primary = False)
def start_film(params):
    name = params.get('text')
    voice = text = 'Не могу найти фильм'
    if name:
        url, title = Media.findPage(name)
        url = Media.getFilm(url)
        if url:
            Media.startFilm(url, title)
            voice = text = 'Включаю'
    return Response(text = text, voice = voice)

@Command.new(['включ* фильм $text', 'включ* фильм*'])
def film(params):
    name = params.get('text')
    if name:
        url, title = Media.findPage(name)
        url = Media.getFilm(url)
        if url:
            Media.startFilm(url, title)
            voice = text = 'Включаю'
        else:
            voice = text = 'Не могу найти фильм'
    else:
        voice = text = 'Какой фильм включить?'
        return Response(text = text, voice = voice, context = [start_film,])
    return Response(text = text, voice = voice)

################################################################################

@Command.new(['$text',], primary = False)
def start_serial(params):
    name = params.get('text')
    voice = text = 'Не могу найти сериал'
    if name:
        url, title = Media.findPage(name)
        seasons = Media.getSerial(url)
        if url:
            Media.startSerial(url, title)
            voice = text = 'Включаю'
    return Response(text = text, voice = voice)

@Command.new(['включ* сериал $text', 'включ* сериал*'])
def serial(params):
    name = params.get('text')
    if name:
        url, title = Media.findPage(name)
        seasons = Media.getSerial(url)
        if url:
            Media.startSerial(seasons, title)
            voice = text = 'Включаю'
        else:
            voice = text = 'Не могу найти'
    else:
        voice = text = 'Какой сериал включить?'
        return Response(text = text, voice = voice, context = [start_film,])
    return Response(text = text, voice = voice)
