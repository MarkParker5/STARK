from typing import Tuple, List, Optional
import os
import json
import re
import requests
import pafy
import screeninfo

from .MediaPlayer import MediaPlayer

class YoutubePlayer(MediaPlayer):

    currentVideoId: str
    playlistItems: list[str]

    def __init__(self, url: str):
        self.currentVideoId, playlistId = self.parse(url)
        if playlistId:
            self.playlistItems = self.getVideosForPlaylist(playlistId)
        if not self.currentVideoId and playlistItems:
            self.currentVideoId = self.playlistItems[0]

    def play(self):
        self.playStreams(*[s.url for s in self.getStreamsForVideo(self.currentVideoId) if s])

    def parse(self, playlistUrl: str) -> tuple[Optional[str], Optional[str]]:
        if match:= re.search(r'youtu.?be(.com\/|\/)((watch\?v=)?(?P<v>[A-z0-9_]+))?(.*?list=(?P<list>[A-z0-9_]+))?', playlistUrl):
            args = match.groupdict()
            return (args.get('v'),  args.get('list'))
        return (None, None)

    def getVideosForPlaylist(self, id: str) -> list[str]:
        parts = ['contentDetails',]#['id' , 'snippet', 'contentDetails']
        api_key = 'AIzaSyBAiOz14QnzYNaUB9uUqvjOM2EoGjUpqvY'

        maxResults = 999     # 50 is max
        received = 0
        nextPageToken = None
        videoIDs = []

        while True:
            result = json.loads(
                requests.get(f'https://youtube.googleapis.com/youtube/v3/playlistItems?part={"&part=".join(parts)}&playlistId={playlistID}&key={api_key}&maxResults={maxResults}&nextPageToken={nextPageToken}',
                    headers = {
                        'Accept':'application/json'
                    }
                ).text
            )

            videoIDs += [res.get('contentDetails').get('videoId') for res in result.get('items')]

            totalCount = result.get('pageInfo').get('totalResults')
            received += result.get('pageInfo').get('resultsPerPage')
            maxResults = totalCount - received

            if maxResults > 0: continue
            else: break

        return videoIDs

    def getStreamsForVideo(self, id: str) -> tuple[str, Optional[str]]:
        ytvideo = pafy.new(self.urlForId(id))

        screenWidth = max([m.width for m in screeninfo.get_monitors()])

        if streams := [s for s in ytvideo.streams if s.dimensions[0] >= screenWidth]:
            return (min(streams, key = lambda s: s.dimensions[0]), None)

        elif streams := [s for s in ytvideo.videostreams if s.dimensions[0] >= screenWidth]:
            return (min(streams, key = lambda s: s.dimensions[0]), ytvideo.getbestaudio())

        else:
            beststream = ytvideo.getbest()
            bestvideostream = ytvideo.getbestvideo()

            if beststream.dimensions[0] >= bestvideostream.dimensions[0]:
                return (beststream, None)
            else:
                return (bestvideostream, ytvideo.getbestaudio())

    def urlForId(self, id: str):
        return f'https://www.youtube.com/watch?v={id}'
