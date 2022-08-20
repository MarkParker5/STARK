from threading import Thread
import websocket
import config
from server.endpoints.ws import WSManager


ws: websocket.WebSocketApp = None
ws_thread: Thread = None
ws_manager = WSManager()

headers = {'Auth': f'Bearer {config.access_token}'}

def on_message(ws, msg):
    print('WS: ', msg)
    ws_manager.handle_message(msg)

def on_open(ws):
    print('WS Open')
    pass

def on_close(ws, status_code, reason):
    start_ws()

def on_error(ws, error):
    # start_ws()
    pass

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
