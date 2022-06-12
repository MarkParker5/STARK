import os, sys

root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(root)

import uvicorn
from API.main import app
from API.endpoints.hub import HubManager
from Raspberry import WiFi


if __name__ == '__main__':
    try:
        hub = HubManager.default().get()
        WiFi.connect_first()
    except:
        WiFi.start_hotspot()

    uvicorn.run('main:app', host = '0.0.0.0', port = 8000, reload = True, reload_dirs=[root,])
