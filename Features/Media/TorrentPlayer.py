from typing import Tuple, List, Optional
import os
import re
import requests
import urllib
from bs4 import BeautifulSoup as BS
import psutil
import screeninfo

from .MediaPlayer import MediaPlayer

class TorrentFile:
    width: int
    height: int
    weight: float
    url: str

class FilmData:
    name: str
    poster: str
    pageUrl: str
    torrentFiles: List[TorrentFile] = []

class TorrentPlayer(MediaPlayer):

    film: FilmData

    localhost = 'http://127.0.0.1:8000/0'

    protocol = 'http://'
    site = 'torr.lafa.site'
    searchPattern = 'https://torr.lafa.site/torrentz/search/{name}/'

    filmSearchSelector = 'div.c_title > a'
    nameSelector = 'td.rightrow.norightborder.notop'
    posterSelector = '#wrapper > table > tbody > tr.cont_tr > td.center_col > table > tbody > tr.film_det > td.fw_imp > div.c_pic_col'
    torrentsSelector = '#tbody_id2 tr:not(.expand-child)'
    torrentsDeskSelector = '#tbody_id2 tr.expand-child'
    weightTorrentSelector = 'td:nth-child(4)'
    linkTorrentSelector = 'td:last-child a.dlink_t'

    @classmethod
    def initWithName(cls, name: str) -> 'TorrentPlayer':
        page = findPage(name)
        film = parsePage(page)

        player = TorrentPlayer()
        player.film = film

        return player

    @staticmethod
    def playUrl(url: str):
        TorrentPlayer.startStream(url)
        TorrentPlayer.playStreams(TorrentPlayer.localhost)

    def play(self):
        torrent = chooseTorrent(self.film)
        self.playUrl(torrent.url)

    def bytesFromString(self, string: str) -> int:
        units = ['KB', 'MB', 'GB', 'PB']

        value = re.search('[0-9]+\.[0-9]+', string)
        if not value: return 0

        number = float(value[0])

        for i, unit in enumerate(units):
            if unit in string:
                return number * 1024 ** (i + 1)\

        return 0

    def get(self, url: str):
        return requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'})

    def findPage(self, name: str) -> Optional[str]:
        response = get(searchPattern.replace('{name}', name))

        page = BS(response.content, 'html.parser')
        link = page.select_one(filmSearchSelector)

        with open('search.html', 'wb') as f: f.write(response.content)
        return protocol + site + link['href'] if link else None

    def parsePage(self, url: Optional[str]) -> Optional[FilmData]:
        if not url: return None

        response = get(url)
        with open('page.html', 'wb') as f: f.write(response.content)
        page = BS(response.content, 'html.parser')

        film = FilmData()
        film.pageUrl = url
        film.name = page.select_one(nameSelector).getText().strip()
        film.poster = page.select_one(posterSelector)

        torrents = page.select(torrentsSelector)
        torrentDesks = page.select(torrentsDeskSelector)

        for torrent, desk in zip(torrents, torrentDesks):
            torrentFile = TorrentFile()

            deskText = desk.getText()
            size = re.search('[0-9]+(x|х)[0-9]+', deskText)
            if not deskText or not size: continue

            if 'x' in size[0]:
                separator = 'x'
            else:
                separator = 'х'

            torrentFile.width, torrentFile.height = [int(s.strip()) for s in size[0].split(separator)]
            weightSpan = torrent.select_one(weightTorrentSelector)
            torrentFile.weight = self.bytesFromString(weightSpan.getText()) if weightSpan else 0

            a =  torrent.select_one(linkTorrentSelector)
            if not a: continue
            torrentFile.url = 'https://' + site + a['href']

            film.torrentFiles.append(torrentFile)

        film.torrentFiles.sort(reverse = True, key = lambda file: file.width)
        return film

    def chooseTorrent(self, film: Optional[FilmData]) -> TorrentFile:
        if not film: return

        path = '/'
        bytes = psutil.disk_usage(path).free

        screenWidth = max([m.width for m in screeninfo.get_monitors()])

        torrents = [torrent for torrent in film.torrentFiles if torrent.weight != 0 and torrent.weight < bytes]

        if matchTorrents := [t for t in torrents if t.width >= screenWidth]:
            return min(matchTorrents, key = lambda t: t.weight) # random.choice(matchTorrents)
        else:
            first = torrents[0]
            torrents = [torrent for torrent in torrents if torrent.width == first.width]
            torrents.sort(key = lambda film: film.weight)

            return torrents[0] # random.choice(torrents)

    @staticmethod
    def startStream(torrentUrl: str):
        file = 'temp.torrent'
        urllib.request.urlretrieve(torrentUrl, file)
        os.system(f'lxterminal --command="webtorrent {file} --stdout"')
