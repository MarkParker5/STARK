from wifi import Cell, Scheme
# from PyAccessPoint import pyaccesspoint
import config


__all__ = [
    'save',
    'get_list',
    'connect_first',
    'save_and_connect',
    'start_hotspot',
    'stop_hotspot',
    'is_hotspot_running'
]

# access_point = pyaccesspoint.AccessPoint()
# access_point.ssid = config.wifi_ssid
# access_point.password = config.wifi_password

class ConnectionException(Exception):
    pass

def get_list() -> list[Cell]:
    return Cell.all('wlan0')

def save(ssid: str, password: str):
    for cell in Cell.all('wlan0'):
        if cell.ssid == ssid:
            Scheme.for_cell('wlan0', ssid, ssid, password).save()
            break

def save_and_connect(ssid: str, password: str):
    for cell in Cell.all('wlan0'):
        if cell.ssid == ssid:
            scheme = Scheme.for_cell('wlan0', ssid, ssid, password)
            scheme.save()
            scheme.activate()

def connect_first() -> None | ConnectionException:
    ssids = [cell.ssid for cell in Cell.all('wlan0')]

    for scheme in Scheme.all():
        ssid = scheme.options.get('wpa-ssid')#, scheme.options.get('wireless-essid'))
        if ssid in ssids:
            scheme.activate()
            break
    else:
        raise ConnectionException('No schemes available')

def start_hotspot():
    # access_point.start()
    ...

def stop_hotspot():
    # access_point.stop()
    ...

def is_hotspot_running() -> bool:
    return False
    # access_point.is_running()
