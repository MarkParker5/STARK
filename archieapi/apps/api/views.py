from django.shortcuts import render
from  django.http import HttpResponse
# Archie
from Command import Command
import modules
import json

def text(request):
    text = request.GET.get("text")
    if not text: return HttpResponse("")
    cmd, params = Command.reg_find(text).values()
    try: response = cmd.start(params)
    except: {'text': f'Ошибка в модуле {cmd.getName()}', 'voice': 'Произошла ошибка'}
    json_string = json.dumps(response)
    return HttpResponse(json_string)

def command(request):
    name = request.GET.get("name")
    params = request.GET.get("params") or {}
    if not name: return HttpResponse("")
    cmd = Command.getCommand(name)
    try: response = cmd.start()
    except: return HttpResponse("")
    if not cmd: return HttpResponse("")
    json_string = json.dumps(response)
    return HttpResponse(json_string)
