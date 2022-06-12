import pathlib
path = str(pathlib.Path(__file__).parent.absolute())
del pathlib


src: str = path + '/resources'

# Api keys

telebot: str
goole_tts_json_key: str = src + '/tts-gc-key.json'

# Speech Recognition

vosk_model: str = src + '/model-small-rus'

# TTS

language_code: str = 'ru-RU'
voice_volume: float = 1

# Archie settings

double_clap_activation: bool = False

# Archie Core

names: list[str] = ['арчи', 'archie']

# DB

db_url: str = 'sqlite:///./sql_app.db'

# WiFi

wifi_ssid: str = 'Archie Hub'
wifi_password: str = '12345678'
