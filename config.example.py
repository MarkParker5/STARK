import pathlib
path = str(pathlib.Path(__file__).parent.absolute())
del pathlib

telebot = '12345678:token'
goole_tts_json_key = path+'google-cloud-text-to-speech-private-key.json'

db_name = 'archie.db'

vosk_model = 'model-small-rus' # from alphacephei.com/vosk/models

double_clap_activation = False

names = ['арчи', 'archie']

#################################################
#                   Django
django_secret_key    = '-----123456789-----'
django_debug         = True
django_allowed_hosts = []
