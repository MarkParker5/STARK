from typing import Tuple, List, Optional
import os
from abc import ABC, abstractmethod

class MediaPlayer(ABC):

    @abstractmethod
    def play(self):
        pass

    @staticmethod
    def playStreams(videoStream: str, audioStream: Optional[str] = None):
        cmd = f'vlc "{videoStream}"'
        if audioStream: cmd += f' --input-slave "{audioStream}"'
        print(cmd)
        os.system(f'lxterminal --command="{cmd}"')

    def addStreamsToQueue(self, videoStream, audioStream):
        pass
