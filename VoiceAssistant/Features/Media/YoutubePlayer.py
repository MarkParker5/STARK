from typing import Tuple, List, Optional
import os
import re
import asyncio
import aiohttp
from aiohttp import ClientSession
from glob import glob
from yt_dlp import YoutubeDL
from .MediaPlayer import MediaPlayer

class YoutubeVideo:
    id: str
    title: str

class YoutubePlaylist:
    id: str
    title: str
    items: [YoutubeVideo]

    def __getitem__(self, item) -> YoutubeVideo:
        return self.items[item]

class YoutubePlayer(MediaPlayer):

    currentVideo: YoutubeVideo
    currentPlaylist: Optional[YoutubePlaylist] = None

    def __init__(self, url: str):
        asyncio.run(self.setup(url))

    async def setup(self, url: str):
        videoId, playlistId = YoutubeAPI.parse(url)

        if playlistId:
            self.currentPlaylist = await YoutubeAPI.getPlaylist(playlistId)
        if videoId and playlistId:
            self.currentVideo = next(filter(lambda video: video.id == videoId, self.currentPlaylist.items), None) or self.currentPlaylist[0]
        elif not videoId and playlistID:
            self.currentVideo = self.currentPlaylist[0]
        else:
            self.currentVideo = await YoutubeAPI.getVideo(videoId)

    def play(self):
        YoutubeAPI.download(YoutubeAPI.urlForId(self.currentVideo.id))
        if path:= YoutubeAPI.pathForId(self.currentVideo.id):
            self.playStreams(path, title = self.currentVideo.title)

class YoutubeAPI:
    baseUrl = 'https://youtube.googleapis.com/youtube/v3'
    api_key = 'AIzaSyBAiOz14QnzYNaUB9uUqvjOM2EoGjUpqvY'

    @staticmethod
    def parse(playlistUrl: str) -> tuple[Optional[str], Optional[str]]:
        if match:= re.search(r'youtu.?be(.com\/|\/)((watch\?v=)?(?P<v>[A-z0-9_]+))?(.*?list=(?P<list>[A-z0-9_]+))?', playlistUrl):
            args = match.groupdict()
            return (args.get('v'),  args.get('list'))
        return (None, None)

    @staticmethod
    async def getVideo(id: str, title: Optional[str] = None) -> YoutubeVideo:
        video = YoutubeVideo()
        video.id = id
        video.title = title or await YoutubeAPI.titleForVideo(id)
        return video

    @staticmethod
    async def getPlaylist(id: str) -> YoutubePlaylist:
        playlist = YoutubePlaylist()
        playlist.id = id
        playlist.title = await YoutubeAPI.titleForPlaylist(id)
        playlist.items = await YoutubeAPI.playlistItems(id)
        return playlist

    @staticmethod
    async def titleForVideo(id: str) -> str:
        params = {
            'key': YoutubeAPI.api_key,
            'part': ['snippet',],
            'id': id,
        }

        if json := await YoutubeAPI.get('videos', params = params):
            return json.get('items')[0].get('snippet').get('title')
        return ''

    @staticmethod
    async def titleForPlaylist(id: str) -> str:
        params = {
            'key': YoutubeAPI.api_key,
            'part': ['snippet',],
            'id': id,
        }

        if json := await YoutubeAPI.get('playlists', params = params):
            return json.get('items')[0].get('snippet').get('title')
        return ''

    @staticmethod
    async def playlistItems(id: str) -> list[YoutubeVideo]:
        maxResults = 999 # 50 is max
        received = 0
        nextPageToken = ''
        videos = []

        while True:
            params = {
                'key': YoutubeAPI.api_key,
                'part': ['contentDetails', 'snippet'],
                'playlistId': id,
                'maxResults': maxResults,
                'nextPageToken': nextPageToken,
            }

            if json := await YoutubeAPI.get('playlistItems', params):
                if error := json.get('error'):
                    pprint(error)
                    print(id, params)
                    exit()

                totalCount = json.get('pageInfo').get('totalResults')
                nextPageToken = json.get('nextPageToken')
                received += json.get('pageInfo').get('resultsPerPage')
                maxResults = totalCount - received

                for item in json.get('items'):
                    videoId = item.get('contentDetails').get('videoId')
                    videoTitle = item.get('snippet').get('title')
                    videos.append(await YoutubeAPI.getVideo(videoId, videoTitle))

            if maxResults > 0: continue
            else: break

        return videos

    @staticmethod
    async def get(url, params) -> 'json':
        url = f'{YoutubeAPI.baseUrl}/{url}'
        headers = {
            'Accept':'application/json'
        }
        async with ClientSession() as session:
            result = await session.get(url, params = params, headers = headers)
            json = await response.json()
            return json
        return None

    @staticmethod
    def urlForId(id: str) -> str:
        return f'https://www.youtube.com/watch?v={id}'

    @staticmethod
    def pathForId(id: str) -> Optional[str]:
        if files := glob(f'./downloads/{id}.*'):
            return files[0]
        return None

    @staticmethod
    def download(url: str):
        with YoutubeDL({
            'format': 'bestvideo[width<=1920][vcodec!=vp9]+bestaudio',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'nopart': True,
            'quiet': True,
            'no_warnings': True,
        }) as ydl:
            ydl.download([url,])

if __name__ == '__main__': main()
