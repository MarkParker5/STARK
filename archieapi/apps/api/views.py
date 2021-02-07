from django.shortcuts import render
from  django.http import HttpResponse
# Archie
from Command import Command
import modules
import json

def index(request):
    text = request.GET.get("text")
    if text == None: return HttpResponse("")
    cmd, params = Command.reg_find(text).values()
    responce = cmd.start(params)
    json_string = json.dumps(responce)
    return HttpResponse(json_string)
