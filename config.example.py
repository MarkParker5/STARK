import pathlib
path = str(pathlib.Path(__file__).parent.absolute())
del pathlib

telebot = '12345678:token'
goole_tts_json_key = path+'google-cloud-text-to-speech-private-key.json'

db_name = 'archie.db'

language_code = 'ru-RU'
device_index  = 1
voice_volume  = 1

energy_threshold = 2000
dynamic_energy_threshold = True
pause_threshold = 1
non_speaking_duration = 1

double_clap_activation = False

names = ['арчи', 'archie']

#################################################
#                   Django
django_secret_key    = '-----123456789-----'
django_debug         = True
django_allowed_hosts = []
