import pathlib
path = str(pathlib.Path(__file__).parent.absolute())
del pathlib

telebot            = '12345678:token'
goole_tts_json_key = path+'google-cloud-text-to-speech-private-key.json'

db_name = 'archie.db'

language_code      = 'ru-RU'
device_index       = 1
voice_volume       = 0.2
double_clap_activation = True

names              = ['арчи', 'archie']

#################################################
#                   Django
django_secret_key    = '-----123456789-----'
django_debug         = True
django_allowed_hosts = []
