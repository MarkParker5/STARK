from threading import Thread

def threadingFunction(func):
    def starter(*args, **kwargs):
        thread = Thread(target = func, args = args, kwargs = kwargs)
        thread.start()
    return starter
