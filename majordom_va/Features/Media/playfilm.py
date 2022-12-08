import requests
from bs4 import BeautifulSoup as BS
import os
from .TorrentPlayer import TorrentPlayer
from VICore import Command, Response

################################################################################
@Command.new(['$name:VIString'])
def playfilm_cb(params):
    return playfilm(params)

@Command.new(['включ* фильм $name:VIString', 'включ* фильм*'])
def playfilm(params):
    name = params.get('name')

    if not name:
        voice = text = 'Какой фильм включить?'
        return Response(text = text, voice = voice, context = [playfilm,])

    text = None
    voice = None

    try:
        player = TorrentPlayer.initWithName(name)
        player.play()
        text = voice = f'Включаю фильм {player.name}'
    except:
        text = voice = f'Что-то пошло не так '

    return Response(text = text, voice = voice)
