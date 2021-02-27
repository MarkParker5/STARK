from .SmartHome import *
from Command import Response
from Command import Command
import os
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
        if os.popen('echo \'pow 0.0.0.0\' | cec-client -s -d 1 |grep power').read() == 'power status: on\n':
            break
    return Response(text = text, voice = voice)

keywords = {}
patterns = []
alarmclock = SmartHome('alarmclock', keywords, patterns)
alarmclock.setStart(method)
