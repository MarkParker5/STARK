class Response:
    def __init__(this, voice, text, callback = None, thread = None):
        this.voice: str = voice
        this.text: str = text
        this.callback: Callback = callback
        this.thread = thread
