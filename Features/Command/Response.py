class Response:
    def __init__(self, voice, text, callback = None, thread = None):
        self.voice: str = voice
        self.text: str = text
        self.callback: Callback = callback
        self.thread = thread
