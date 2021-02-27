from .SmartHome import *
from Command import Response
from Command import Command
################################################################################

def method(params):
    Command.getCommand('tv on').start({})
    Command.getCommand('window_open').start({})
    shedule = Command.getCommand('Todays Shedule').start({}).voice
    time = Command.getCommand('Current Time').start({}).voice
    voice = f'Доброе утро! {time}.'
    if shedule:
        voice = voice + ' Расписание на сегодня: ' + shedule
    while True:
        if os.system('echo \'pow 0.0.0.0\' | cec-client -s -d 1 |grep power') == 'power status: on':
            break
    return Response(text = text, voice = voice)

keywords = {}
patterns = []
alarmclock = SmartHome('alarmclock', keywords, patterns)
alarmclock.setStart(method)
