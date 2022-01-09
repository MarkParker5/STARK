from typing import Tuple, List, Optional
import os
from abc import ABC, abstractmethod

class MediaPlayer(ABC):

    @abstractmethod
    def play(self):
        pass

    @staticmethod
    def playStreams(videoStream: str, audioStream: Optional[str] = None, title: Optional[str] = None):
        cmd = f'vlc "{videoStream}" --fullscreen'
        if audioStream: cmd += f' --input-slave "{audioStream}"'
        if title: cmd += f' --meta-title "{title}"'
        os.system(f'lxterminal --command=\'{cmd}\'')

    def addStreamsToQueue(self, videoStream, audioStream):
        pass
