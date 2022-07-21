import os
import config
import pathlib
from SmartHome.Raspberry import WiFi

path = str(pathlib.Path(__file__).parent.absolute())
src: str = path + '/resources'

files = []
files.append(f'{src}/jwt-key.pub')
files.append(f'{src}/jwt_access_token')
files.append(f'{src}/jwt_refresh_token')
files.append(f'{src}/database.sqlite3')

for file in files:
    try:
        os.remove(config.access_token)
    except:
        pass

WiFi.networks = []
WiFi.write_networks()
WiFi.reconnect()
WiFi.start_hotspot()
WiFi.start_wps()
