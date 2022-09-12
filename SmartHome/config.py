import pathlib
path = str(pathlib.Path(__file__).parent.absolute())
del pathlib


src: str = path + '/resources'

# DB

db_url: str = f'sqlite:///{src}/database.sqlite3'
db_async_url: str = f'sqlite+aiosqlite:///{src}/database.sqlite3'

# WiFi

# TODO: hostapd.conf
# wifi_ssid: str = 'Archie Hub'
# wifi_password: str = '12345678'

# API

api_url = 'https://home.parker-programs.com/api'
ws_url = 'wss://home.parker-programs.com/ws/hub'
localhost = 'http://localhost:8000'

try:
    with open(f'{src}/jwt-key.pub', 'r') as f:
        public_key = f.read()
except FileNotFoundError:
    public_key = ''

try:
    with open(f'{src}/jwt_access_token', 'r') as f:
        access_token = f.read()
except FileNotFoundError:
    access_token = ''

try:
    with open(f'{src}/jwt_refresh_token', 'r') as f:
        refresh_token = f.read()
except FileNotFoundError:
    refresh_token = ''

algorithm = 'RS256'
