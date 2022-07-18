import os
import subprocess
import re
from dataclasses import dataclass
import time


__all__ = [
    'start_hotspot_if_needed',
    'scan',
    'save',
    'start_wps',
    'start_hotspot',
    'stop_hotspot',
    'InterfaceBusyException'
]

network_regex = re.compile(
    r'network=\{\s+ssid="(?P<ssid>.*)"\s+psk="(?P<psk>.*)"\s+id_str="(?P<id_str>.*)"\s+\}'
)

cell_regex = re.compile(
    r'Cell(?:.|\n)*?Frequency:(?P<frequency>.+)(?:.|\n)*?Quality=(?P<quality>.+)(?:.|\n)*?Encryption key:(?P<encrypted>.+)(?:.|\n)*?ESSID:"(?P<ssid>.+)"'
)

wpa_supplicant_path = r'/etc/wpa_supplicant/wpa_supplicant.conf'
interfaces_path = r'/etc/network/interfaces'

wpa_supplicant_header = '''
country=DE
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
ap_scan=1
update_config=1
'''

interfaces_header = '''
source-directory /etc/network/interfaces.d

auto lo
auto eth0
auto wlan0
auto ap0

iface eth0 inet dhcp
iface lo inet loopback

allow-hotplug ap0
iface ap0 inet static
    address 192.168.10.1
    netmask 255.255.255.0
    hostapd /etc/hostapd/hostapd.conf

allow-hotplug wlan0
iface wlan0 inet manual
    wpa-roam /etc/wpa_supplicant/wpa_supplicant.conf
'''

class InterfaceBusyException(Exception):
    pass

@dataclass
class Cell():
    ssid: str
    quality: float
    frequency: str
    encrypted: bool
    #encryption_type: str

@dataclass
class Network:
    ssid: str
    psk: str
    id_str: str = ''

networks: Network = []
is_hotspot_running = False

def read_saved_networks():
    with open(wpa_supplicant_path, 'r') as f:
        for match in network_regex.finditer(f.read()):
            networks.append(
                Network(
                    **match.groupdict()
                )
            )

def write_networks():
    with open(wpa_supplicant_path, 'w') as f:
        f.write(wpa_supplicant_header)
        for i, network in enumerate(networks):
            f.write(f'''
network={{
        ssid="{network.ssid}"
        psk="{network.psk}"
        id_str="AP{i}"
}}''')
    with open(interfaces_path, 'w') as f:
        f.write(interfaces_header)
        for i in range(len(networks)):
            f.write(f'iface AP{i} inet dhcp')

def reconnect():
    os.system('sudo wpa_cli -i wlan0 reconfigure')

def is_connected() -> bool:
    try:
        return bool(subprocess.check_output(['iwgetid',]))
    except subprocess.CalledProcessError:
        return False

def start_hotspot():
    os.system('service hostapd stop')
    os.system('service dnsmasq stop')
    os.system('service dhcpcd stop')
    os.system('iw dev wlan0 interface add ap0 type __ap')
    os.system('service hostapd start')
    os.system('service dnsmasq start')
    os.system('service dhcpcd start')

def stop_hotspot():
    os.system('sudo service hostapd stop')

# Public

def start_hotspot_if_needed():
    global is_hotspot_running
    connected = is_connected()
    if not connected and not is_hotspot_running:
        start_hotspot()
        is_hotspot_running = True
    elif connected and is_hotspot_running:
        stop_hotspot()
        time.sleep(10)
        is_hotspot_running = False

def save(ssid: str, password: str):
    # read_saved_networks()
    networks.append(Network(ssid, password))
    write_networks()
    reconnect()

def start_wps():
    os.system('wpa_cli -i wlan0 wps_pbc')

def scan() -> list[Cell]:
    try:
        output = subprocess.check_output('sudo iwlist wlan0 scan'.split(' '), text = True)
    except subprocess.CalledProcessError as exc:
        raise InterfaceBusyException from exc

    for match in cell_regex.finditer(output):
        match = match.groupdict()

        quality, max = map(float, match['quality'].split(' ')[0].split('/'))

        ssid = match['ssid'].strip()
        quality = round(quality / max, 2)
        frequency = re.sub(r'\(Channel.*\)', '',  match['frequency']).strip()
        encrypted = match['encrypted'] == 'on'

        yield Cell(ssid, quality, frequency, encrypted)

# Main

if __name__ == '__main__':
    start_hotspot_if_needed()
