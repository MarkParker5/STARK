import uvicorn
from server import app
from client import client, ws
from hardware import WiFi


def run():
    ws.start()
    client.fetch()

    # try:
    #     WiFi.connect_first()
    # except: # TODO: specify wifi exception
    #     WiFi.start_hotspot()
    # finally:
    #     print('complete')

    uvicorn.run('main:app', host = '0.0.0.0', port = 8000, reload = False)

if __name__ == '__main__':
    run()
