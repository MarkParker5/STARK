from .Raspi import *
from VICore import Command, Response

################################################################################

@Command.new(['включи* (телевизор|экран)'])
def tv_on(params):
    Raspi.hdmi_cec('on 0')
    Raspi.hdmi_cec('as')
    voice = text = ''
    return Response(text = text, voice = voice)

################################################################################

@Command.new(['(выключи|отключи)* (телевизор|экран)'])
def tv_off(params):
    Raspi.hdmi_cec('standby 0')
    voice = text = ''
    return Response(text = text, voice = voice)

################################################################################

@Command.new(['* (выведи|вывести|покажи|открой|показать|открыть) * с (провода|hdmi|кабеля|порта) * $num *'])
def tv_hdmi_source(params):
    port = params['num'] + '0' if len(params['num']) == 1 else params['num']
    Raspi.hdmi_cec(f'tx 4F:82:{port}:00')
    voice = text = ''
    return Response(text = text, voice = voice)

################################################################################

@Command.new(['* (выведи|вывести|покажи|открой|показать|открыть) * с (ноута|ноутбука|планшета|провода|hdmi)'])
def tv_hdmi_2(params):
    Raspi.hdmi_cec('tx 4F:82:20:00')
    voice = text = ''
    return Response(text = text, voice = voice)

################################################################################

@Command.new(['* (верни|вернуть|включи*|покажи|показать) [основн|нормальн|стандартн|привычн]* (телевизор|экран|картинк|изображение) *'])
def tv_hdmi_main(params):
    Raspi.hdmi_cec('as')
    voice = text = ''
    return Response(text = text, voice = voice)
