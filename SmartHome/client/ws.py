from threading import Thread
import websocket
import config
from server.endpoints.ws import WSManager


ws: websocket.WebSocketApp = None
ws_thread: Thread = None
ws_manager = WSManager()

headers = {'Authorization': f'Bearer {config.access_token}'}

def on_message(ws, msg):
    if response := ws_manager.handle_message(msg):
        ws.send(response)

def on_open(ws):
    pass

def on_close(ws, status_code, reason):
    start()

def on_error(ws, error):
    pass # TODO: log

def start():
    global ws, ws_thread

    if ws: ws.close()

    ws = websocket.WebSocketApp(config.ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        header=headers
    )

    ws_thread = Thread(target=ws.run_forever)
    ws_thread.start()
