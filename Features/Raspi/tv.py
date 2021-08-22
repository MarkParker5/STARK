from .Raspi import *
from ..Command import Response
################################################################################
def method(params):
    Raspi.hdmi_cec('on 0')
    Raspi.hdmi_cec('as')
    voice = text = ''
    return Response(text = text, voice = voice)

keywords = {}
patterns = ['* включи* (телевизор|экран) *']
tv_on = Raspi('tv on', keywords, patterns)
tv_on.setStart(method)
################################################################################
def method(params):
    Raspi.hdmi_cec('standby 0')
    voice = text = ''
    return Response(text = text, voice = voice)

keywords = {}
patterns = ['* (выключи|отключи)* (телевизор|экран) *']
tv_off = Raspi('tv off', keywords, patterns)
tv_off.setStart(method)
################################################################################
def method(params):
    port = params['num'] + '0' if len(params['num']) == 1 else params['num']
    Raspi.hdmi_cec(f'tx 4F:82:{port}:00')
    voice = text = ''
    return Response(text = text, voice = voice)

keywords = {}
patterns = ['* (выведи|вывести|покажи|открой|показать|открыть) * с (провода|hdmi|кабеля|порта) * $num *']
tv_hdmi = Raspi('tv hdmi source', keywords, patterns)
tv_hdmi.setStart(method)
################################################################################
def method(params):
    Raspi.hdmi_cec('tx 4F:82:20:00')
    voice = text = ''
    return Response(text = text, voice = voice)

keywords = {}
patterns = ['* (выведи|вывести|покажи|открой|показать|открыть) * с (ноута|ноутбука|планшета|провода|hdmi)']
tv_hdmi = Raspi('tv hdmi source', keywords, patterns)
tv_hdmi.setStart(method)
################################################################################
def method(params):
    Raspi.hdmi_cec('as')
    voice = text = ''
    return Response(text = text, voice = voice)

keywords = {}
patterns = ['* (верни|вернуть|включи*|покажи|показать) [основн|нормальн|стандартн|привычн]* (телевизор|экран|картинк|изображение) *']
tv_rpi = Raspi('tv rpi source', keywords, patterns)
tv_rpi.setStart(method)
